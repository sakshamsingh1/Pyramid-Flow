#!/bin/bash

# This script is used for batch extract the vae latents for video generation training
# Since the video latent extract is very slow, pre-extract the video vae latents will save the training time

GPUS=1  # The gpu number
MODEL_NAME=pyramid_mmdit     # The model name, `pyramid_flux` or `pyramid_mmdit`
VAE_MODEL_PATH=/mnt/sda1/saksham/TI2AV/pyramid/causal_video_vae  # The VAE CKPT dir.
ANNO_FILE=/home/sxk230060/TI2AV/Pyramid-Flow/annotation/train.json   # The video annotation file path
WIDTH=256
HEIGHT=256
NUM_FRAMES=17
FPS=8

torchrun --nproc_per_node $GPUS \
    tools/extract_video_vae_latents.py \
    --batch_size 1 \
    --model_dtype bf16 \
    --model_path $VAE_MODEL_PATH \
    --anno_file $ANNO_FILE \
    --width $WIDTH \
    --height $HEIGHT \
    --num_frames $NUM_FRAMES \
    --fps $FPS