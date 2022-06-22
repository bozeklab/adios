python main_pretrain.py \
    --alpha_entropy 0. \
    --alpha_sparsity 0.8269158678071891 \
    --batch_size 64 \
    --classifier_lr 0.1 \
    --lr 0.44397171059658247 \
    --mask_lr 0.20463999909125877 \
    --weight_decay 1e-05 \
    --scheduler warmup_cosine \
    --optimizer sgd \
    --max_epochs 200 \
    --dataset stl10 \
    --N 6 \
    --encoder vit_tiny \
    --mask_fbase 32 \
    --method byol_adios \
    --output_dim 256 \
    --pred_hidden_dim 8192 \
    --proj_hidden_dim 4096 \
    --unet_norm gn \
    --gpus 0 \
    --data_dir /datasets/yshi \
    --wandb_dir /datasets/yshi/adios \
    --checkpoint_dir /datasets/yshi/adios/trained_models \
    --project adios \
    --entity yugeten \
    --name byol_adios_vit_stl10 \
    --wandb True
# note: replace --data_dir, --wandb_dir, --checkpoint_dir, --project, --entity, --name with your custom values.
