import os
import sys
sys.path.append(os.path.abspath('.'))

import argparse
import datetime
import numpy as np
import time
import torch
import io
import json
import jsonlines

import cv2
import math
import random
from pathlib import Path
from tqdm import tqdm

from concurrent import futures
from torch.utils.data import Dataset, DataLoader, DistributedSampler
from collections import OrderedDict
from torchvision import transforms as pth_transforms
from torchvision.transforms.functional import InterpolationMode

from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

from trainer_misc import init_distributed_mode
from video_vae import CausalVideoVAELossWrapper

def get_transform(width, height, new_width=None, new_height=None, resize=False,):
    transform_list = []
    if resize:
        if new_width is None:
            new_width = width // 8 * 8
        if new_height is None:
            new_height = height // 8 * 8
        transform_list.append(pth_transforms.Resize((new_height, new_width), InterpolationMode.BICUBIC, antialias=True))
    transform_list.extend([
        pth_transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
    ])
    transform_list = pth_transforms.Compose(transform_list)
    return transform_list

def load_video_and_transform(video_path, frame_number, new_width=None, new_height=None, max_frames=600, sample_fps=24, resize=False):
    try:
        video_capture = cv2.VideoCapture(video_path)
        fps = video_capture.get(cv2.CAP_PROP_FPS)
        frames = []
        while True:
            flag, frame = video_capture.read()
            if not flag:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = torch.from_numpy(frame)
            frame = frame.permute(2, 0, 1)
            frames.append(frame)
            if len(frames) >= max_frames:
                break
        video_capture.release()
        interval = max(int(fps / sample_fps), 1)
        frames = frames[::interval][:frame_number]
        frames = torch.stack(frames).float() / 255
        width = frames.shape[-1]
        height = frames.shape[-2]
        video_transform = get_transform(width, height, new_width, new_height, resize=resize)
        frames = video_transform(frames)
        if resize:
            if new_width is None:
                new_width = width // 32 * 32
            if new_height is None:
                new_height = height // 32 * 32
        return frames
    except Exception:
        return None

class VideoDataset(Dataset):
    def __init__(self, anno_file, width, height, num_frames, num_items=-1, fps=8):
        super().__init__()
        self.annotation = []
        self.width = width
        self.height = height
        self.num_frames = num_frames
        self.fps = fps

        with jsonlines.open(anno_file, 'r') as reader:
            for item in tqdm(reader):
                self.annotation.append(item)

        if num_items > 0:
            self.annotation = self.annotation[:num_items]        

        tot_len = len(self.annotation)
        print(f"Totally {len(self.annotation)} videos")

    def process_one_video(self, video_item):
        videos_per_task = []
        video_path = video_item['video']
        output_latent_path = video_item['latent']

        try:
            video_frames_tensors = load_video_and_transform(
                video_path, 
                # frame_indexs, 
                frame_number=self.num_frames,    # The num_frames to encode
                new_width=self.width, 
                new_height=self.height, 
                sample_fps=self.fps,
                resize=True
            )

            if video_frames_tensors is None:
                return videos_per_task

            video_frames_tensors = video_frames_tensors.permute(1, 0, 2, 3).unsqueeze(0)
            # video_frames_tensors = video_frames_tensors.unsqueeze(0)
            videos_per_task.append({'video': video_path, 'input': video_frames_tensors, 'output': output_latent_path})

        except Exception as e:
            print(f"Load video tensor ERROR: {e}")

        return videos_per_task

    def __getitem__(self, index):
        try:
            video_item = self.annotation[index]
            videos_per_task = self.process_one_video(video_item)
        except Exception as e:
            print(f'Error with {e}')
            videos_per_task = []

        return videos_per_task

    def __len__(self):
        return len(self.annotation)

def get_args():
    parser = argparse.ArgumentParser('Pytorch Multi-process Training script', add_help=False)
    parser.add_argument('--batch_size', default=4, type=int)
    parser.add_argument('--model_path', default='', type=str, help='The pre-trained weight path')
    parser.add_argument('--model_dtype', default='bf16', type=str, help="The Model Dtype: bf16 or df16")
    parser.add_argument('--anno_file', type=str, default='', help="The video annotation file")
    parser.add_argument('--width', type=int, default=640, help="The video width")
    parser.add_argument('--height', type=int, default=384, help="The video height")
    parser.add_argument('--num_frames', type=int, default=121, help="The frame number to encode")
    parser.add_argument('--save_memory', action='store_true', help="Open the VAE tiling")
    parser.add_argument('--num_items', type=int, default=-1, help="The video height")
    parser.add_argument('--fps', type=int, default=8, help="The video height")

    return parser.parse_args()

def build_model(args):
    model_path = args.model_path
    model_dtype = args.model_dtype
    model = CausalVideoVAELossWrapper(model_path, model_dtype=model_dtype, interpolate=False, add_discriminator=False)
    model = model.eval()
    return model


def build_data_loader(args):

    def collate_fn(batch):
        return_batch = {'input' : [], 'output': []}
        for videos_ in batch:
            for video_input in videos_:
                return_batch['input'].append(video_input['input'])
                return_batch['output'].append(video_input['output'])
        return return_batch

    dataset = VideoDataset(args.anno_file, args.width, args.height, args.num_frames, args.num_items, args.fps)
    sampler = DistributedSampler(dataset, num_replicas=args.world_size, rank=args.rank, shuffle=False)
    loader = DataLoader(
        dataset, batch_size=args.batch_size, num_workers=6, pin_memory=True, 
        sampler=sampler, shuffle=False, collate_fn=collate_fn, drop_last=False, prefetch_factor=2,
    )
    return loader


def save_tensor(tensor, output_path):
    try:
        torch.save(tensor.clone(), output_path)
    except Exception as e:
        pass


def main():
    args = get_args()
    
    init_distributed_mode(args)

    device = torch.device('cuda')
    rank = args.rank

    model = build_model(args)
    model.to(device)

    if args.model_dtype == "bf16":
        torch_dtype = torch.bfloat16 
    elif args.model_dtype == "fp16":
        torch_dtype = torch.float16
    else:
        torch_dtype = torch.float32

    data_loader = build_data_loader(args)
    torch.distributed.barrier()

    window_size = 16
    temporal_chunk = True
    task_queue = []

    if args.save_memory:
        # Open the tiling, to reduce gpu memory cost
        model.vae.enable_tiling()

    with futures.ThreadPoolExecutor(max_workers=16) as executor:

        for sample in tqdm(data_loader):
            input_video_list = sample['input']
            output_path_list = sample['output']

            with torch.no_grad(), torch.cuda.amp.autocast(enabled=True, dtype=torch_dtype):
                for video_input, output_path in zip(input_video_list, output_path_list):
                    video_latent = model.encode_latent(video_input.to(device), sample=True, window_size=window_size, temporal_chunk=temporal_chunk, tile_sample_min_size=256)
                    video_latent = video_latent.to(torch_dtype).cpu()
                    task_queue.append(executor.submit(save_tensor, video_latent, output_path))
        
        for future in futures.as_completed(task_queue):
            res = future.result()

    torch.distributed.barrier()

if __name__ == "__main__":
    main()