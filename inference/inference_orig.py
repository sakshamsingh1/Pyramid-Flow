import os
import json
import torch
import PIL
from PIL import Image
from pyramid_dit import PyramidDiTForVideoGeneration
from diffusers.utils import export_to_video
import json

variant='diffusion_transformer_384p'       # For low resolution variant

model_name = "pyramid_mmdit"   # select the model "pyramid_flux" or "pyramid_mmdit"

model_path = "/mnt/user/saksham/TI2AV/misc/Pyramid-Flow_old/ckpts/pyramid-flow-sd3"   # The downloaded checkpoint dir
model_dtype = 'bf16'

device_id = 0
torch.cuda.set_device(device_id)

model = PyramidDiTForVideoGeneration(
    model_path,
    model_dtype,
    model_name=model_name,
    model_variant=variant,
)

model.vae.to("cuda")
model.dit.to("cuda")
model.text_encoder.to("cuda")

model.vae.enable_tiling()

if model_dtype == "bf16":
    torch_dtype = torch.bfloat16 
elif model_dtype == "fp16":
    torch_dtype = torch.float16
else:
    torch_dtype = torch.float32

def resize_crop_image(img: PIL.Image.Image, tgt_width, tgt_height):
    ori_width, ori_height = img.width, img.height
    scale = max(tgt_width / ori_width, tgt_height / ori_height)
    resized_width = round(ori_width * scale)
    resized_height = round(ori_height * scale)
    img = img.resize((resized_width, resized_height), resample=PIL.Image.LANCZOS)

    left = (resized_width - tgt_width) / 2
    top = (resized_height - tgt_height) / 2
    right = (resized_width + tgt_width) / 2
    bottom = (resized_height + tgt_height) / 2

    # Crop the center of the image
    img = img.crop((left, top, right, bottom))
    
    return img

# read_dir = '/mnt/data2/saksham/i2av/pyramid/asva_input_384_640'
read_dir = '/mnt/data2/saksham/i2av/asva_eval/image_orig'
save_dir = '/mnt/data2/saksham/i2av/pyramid/i2v_384_640_orig'
path = '/mnt/data2/saksham/i2av/asva_eval/file_prompt_map.json'
data = json.load(open(path))
DRY_RUN = False
count = 0

for file, prompt in data.items():

    image_path = os.path.join(read_dir, file+'.jpg')
    image = Image.open(image_path).convert("RGB")
    save_path = os.path.join(save_dir, file+'.mp4')

    # used for 384p model variant
    width = 640
    height = 384

    temp = 16
    image = image.resize((width, height))
    image = resize_crop_image(image, width, height)

    with torch.no_grad(), torch.cuda.amp.autocast(enabled=True if model_dtype != 'fp32' else False, dtype=torch_dtype):
        frames = model.generate_i2v(
            prompt=prompt,
            input_image=image,
            num_inference_steps=[10, 10, 10],
            temp=temp,
            guidance_scale=7.0,
            video_guidance_scale=4.0,
            output_type="pil",
            save_memory=True,         # If you have enough GPU memory, set it to `False` to improve vae decoding speed
        )

    export_to_video(frames, save_path, fps=24)

    if DRY_RUN and count > 5:
        break

    count += 1