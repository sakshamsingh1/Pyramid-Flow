import os
import json
from tqdm import tqdm

metas = [] 
video_dir = '/mnt/sda1/saksham/TI2AV/AVSync15/videos'
save_dir = '/mnt/sda1/saksham/TI2AV/AVSync15/latent'
save_text_dir = '/mnt/sda1/saksham/TI2AV/AVSync15/text_fea'
meta_file = '/mnt/sda1/saksham/TI2AV/AVSync15/train.txt'
output_file = '/home/sxk230060/TI2AV/Pyramid-Flow/annotation/train.json'
with open(meta_file, 'r') as f:
    for line in f:
        metas.append(line.strip())

def get_text(meta):
    text = meta.split('/')[0].replace('__', ' ').replace('_', ' ')
    return text

for meta in tqdm(metas):
    info = {}
    info['video'] = os.path.join(video_dir, meta)
    info['latent'] = os.path.join(save_dir, os.path.basename(meta).replace('.mp4', '.pt'))
    info['text'] = get_text(meta)
    info['text_fea'] = os.path.join(save_text_dir, os.path.basename(meta).split('.')[0]+'_text.pt')
    with open(output_file, 'a') as f:
        json.dump(info, f)
        f.write('\n')        