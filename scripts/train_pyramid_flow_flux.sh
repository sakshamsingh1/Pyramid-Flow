#!/bin/bash

# This script is used for Pyramid-Flow Video Generation Training (Using Temporal Pyramid and autoregressive training)
# It enables the autoregressive video generative training with temporal pyramid
# make sure to set, NUM_FRAMES % VIDEO_SYNC_GROUP == 0; GPUS % VIDEO_SYNC_GROUP == 0

GPUS=2  # The gpu number
SHARD_STRATEGY=zero2   # zero2 or zero3
VIDEO_SYNC_GROUP=4     # values in [4, 8, 16] The number of process that accepts the same input video, used for temporal pyramid AR training.
MODEL_NAME=pyramid_flux     # The model name, `pyramid_flux` or `pyramid_mmdit`
MODEL_PATH=/mnt/sda1/saksham/TI2AV/pyramid_flux/  # The downloaded ckpt dir. IMPORTANT: It should match with model_name, flux or mmdit (sd3)
VARIANT=diffusion_transformer_384p  # The DiT Variant
OUTPUT_DIR=/mnt/sda1/saksham/TI2AV/ckpts-pyramid-flux-ar  # The checkpoint saving dir

if [ -d "$OUTPUT_DIR" ]; then
    echo "Removing existing directory: $OUTPUT_DIR"
    rm -rf "$OUTPUT_DIR"
fi

BATCH_SIZE=4    # It should satisfy batch_size % 4 == 0
GRAD_ACCU_STEPS=2
RESOLUTION="256p"     # 384p or 768p
NUM_FRAMES=4         # e.g., 16 for 5s, 32 for 10s
ANNO_FILE=/home/sxk230060/TI2AV/Pyramid-Flow/annotation/train.json  # The video annotation file path

# For the 768p version, make sure to add the args:  --gradient_checkpointing

CUDA_VISIBLE_DEVICES=0,1 torchrun --nproc_per_node $GPUS \
    train/train_pyramid_flow.py \
    --num_workers 8 \
    --task t2v \
    --use_fsdp \
    --fsdp_shard_strategy $SHARD_STRATEGY \
    --use_temporal_causal \
    --use_temporal_pyramid \
    --interp_condition_pos \
    --sync_video_input \
    --video_sync_group $VIDEO_SYNC_GROUP \
    --load_text_encoder \
    --model_name $MODEL_NAME \
    --model_path $MODEL_PATH \
    --model_dtype bf16 \
    --model_variant $VARIANT \
    --schedule_shift 1.0 \
    --gradient_accumulation_steps $GRAD_ACCU_STEPS \
    --output_dir $OUTPUT_DIR \
    --batch_size $BATCH_SIZE \
    --max_frames $NUM_FRAMES \
    --resolution $RESOLUTION \
    --anno_file $ANNO_FILE \
    --frame_per_unit 1 \
    --lr_scheduler constant_with_warmup \
    --opt adamw \
    --opt_beta1 0.9 \
    --opt_beta2 0.95 \
    --seed 42 \
    --weight_decay 1e-4 \
    --clip_grad 1.0 \
    --lr 5e-5 \
    --warmup_steps 1000 \
    --epochs 40 \
    --iters_per_epoch 2000 \
    --report_to wandb \
    --print_freq 40 \
    --save_ckpt_freq 2 \
    --load_vae \
    --load_vae_latent \
    --sp_proc_num 16