import os
import json
from tqdm import tqdm

metas = [] 
video_dir = '/mnt/sda1/saksham/TI2AV/AVSync15/videos'
save_dir = '/mnt/sda1/saksham/TI2AV/AVSync15/latent'
save_text_dir = '/mnt/sda1/saksham/TI2AV/AVSync15/text_fea'
meta_file = '/mnt/sda1/saksham/TI2AV/AVSync15/train.txt'
text_caption_file = '/mnt/sda1/saksham/TI2AV/AVSync15/cog_train_caption.json'
output_file = '/home/sxk230060/TI2AV/Pyramid-Flow/annotation/train.json'
with open(meta_file, 'r') as f:
    for line in f:
        metas.append(line.strip())

text_captions = json.load(open(text_caption_file, 'r'))

def get_text_label(meta):
    text = meta.split('/')[0].replace('__', ' ').replace('_', ' ')
    return text

def get_text_caption(meta):
    text = text_captions[meta]
    return text

for meta in tqdm(metas):
    info = {}
    info['video'] = os.path.join(video_dir, meta)
    info['latent'] = os.path.join(save_dir, os.path.basename(meta).replace('.mp4', '.pt'))
    info['text'] = get_text_caption(os.path.basename(meta).replace('.mp4', ''))
    info['text_fea'] = os.path.join(save_text_dir, os.path.basename(meta).replace('.mp4', '.pt'))
    with open(output_file, 'a') as f:
        json.dump(info, f)
        f.write('\n')        