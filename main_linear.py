import os
import json
from pathlib import Path

from pytorch_lightning import Trainer
from pytorch_lightning.callbacks import LearningRateMonitor
from pytorch_lightning.loggers import WandbLogger
from pytorch_lightning.plugins import DDPPlugin

from src.args.setup import parse_args_linear
from src.args.utils import IMG_SIZE_DATASET

try:
    from src.methods.dali import ClassificationABC
except ImportError:
    _dali_avaliable = False
else:
    _dali_avaliable = True
from src.methods.linear import LinearModel
from src.utils.classification_dataloader import prepare_data
from src.utils.checkpointer import Checkpointer
from src.methods import METHODS


def main():
    args = parse_args_linear()

    # build paths
    ckpt_dir = Path(args.pretrained_feature_extractor)
    args_path = ckpt_dir / "args.json"
    ckpt_path = [ckpt_dir / ckpt for ckpt in os.listdir(ckpt_dir) if ckpt.endswith(".ckpt")][0]

    # load arguments
    with open(args_path) as f:
        method_args = json.load(f)

    # build the model
    model = METHODS[method_args["method"]].load_from_checkpoint(
        ckpt_path, strict=False, **method_args
    )

    if args.dali:
        assert _dali_avaliable, "Dali is not currently avaiable, please install it first."
        MethodClass = type(f"Dali{LinearModel.__name__}", (LinearModel, ClassificationABC), {})
    else:
        MethodClass = LinearModel

    model = MethodClass(model, **args.__dict__)

    train_loader, val_loader = prepare_data(
        dataset=args.dataset,
        size=IMG_SIZE_DATASET[args.dataset],
        data_dir=args.data_dir,
        batch_size=args.batch_size,
        num_workers=args.num_workers,
    )

    callbacks = []

    # wandb logging
    if args.wandb:
        wandb_logger = WandbLogger(
            name=args.name, project=args.project, entity=args.entity, offline=args.offline
        )
        wandb_logger.watch(model, log="gradients", log_freq=100)
        wandb_logger.log_hyperparams(args)

        # lr logging
        lr_monitor = LearningRateMonitor(logging_interval="epoch")
        callbacks.append(lr_monitor)

        # save checkpoint on last epoch only
        ckpt = Checkpointer(
            args,
            logdir=os.path.join(args.pretrained_feature_extractor, "linear"),
            frequency=args.checkpoint_frequency,
        )
        callbacks.append(ckpt)

    trainer = Trainer.from_argparse_args(
        args,
        logger=wandb_logger if args.wandb else None,
        callbacks=callbacks,
        plugins=DDPPlugin(find_unused_parameters=False),
        checkpoint_callback=False,
        terminate_on_nan=True,
        accelerator="ddp",
    )
    if args.dali:
        trainer.fit(model, val_dataloaders=val_loader)
    else:
        trainer.fit(model, train_loader, val_loader)


if __name__ == "__main__":
    main()
