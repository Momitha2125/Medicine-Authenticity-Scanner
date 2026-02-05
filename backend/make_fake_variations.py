# make_fake_variations_all.py
# Scans dataset/train/real for images (any extension), and creates fake variations for each.
# Output:
#   dataset/train/fake/
#   dataset/val/fake/
#
# Usage: run from the backend folder (where dataset/ exists).
# Make sure Pillow, numpy, opencv-python installed in venv:
# pip install pillow numpy opencv-python

import os, random
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import numpy as np

# CONFIG
SRC_DIR = "dataset/train/real"    # source real images (will iterate all image files here)
OUT_TRAIN = "dataset/train/fake"
OUT_VAL = "dataset/val/fake"
N_PER_IMAGE = 8   # number of fake variations to create per source image
VAL_RATIO = 0.2   # fraction of generated images that go to validation
IMG_SIZE = (224,224)  # resize output images

os.makedirs(OUT_TRAIN, exist_ok=True)
os.makedirs(OUT_VAL, exist_ok=True)

def add_noise_pil(img, strength=0.05):
    arr = np.array(img).astype(np.float32)/255.0
    noise = np.random.normal(0, strength, arr.shape).astype(np.float32)
    arr = arr + noise
    arr = np.clip(arr, 0, 1)
    arr = (arr*255).astype(np.uint8)
    return Image.fromarray(arr)

def random_edit(img):
    w,h = img.size
    # crop/scale
    if random.random() < 0.6:
        cx = random.uniform(0.85, 1.0)
        cy = random.uniform(0.85, 1.0)
        nw, nh = int(w*cx), int(h*cy)
        x = random.randint(0, max(0, w-nw))
        y = random.randint(0, max(0, h-nh))
        img = img.crop((x,y,x+nw,y+nh)).resize((w,h), Image.BILINEAR)
    # rotate small
    if random.random() < 0.5:
        angle = random.uniform(-10, 10)
        img = img.rotate(angle, expand=False, fillcolor=(255,255,255))
    # color jitter
    if random.random() < 0.8:
        if random.random() < 0.6:
            img = ImageEnhance.Brightness(img).enhance(random.uniform(0.6, 1.4))
        if random.random() < 0.6:
            img = ImageEnhance.Contrast(img).enhance(random.uniform(0.6, 1.4))
        if random.random() < 0.5:
            img = ImageEnhance.Color(img).enhance(random.uniform(0.3, 1.6))
    # blur/sharp
    r = random.random()
    if r < 0.25:
        img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.6, 2.0)))
    elif r < 0.4:
        img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=3))
    # add noise
    if random.random() < 0.6:
        img = add_noise_pil(img, strength=random.uniform(0.02,0.12))
    # overlay a sticker/rectangle to simulate tampering
    if random.random() < 0.45:
        draw = ImageDraw.Draw(img)
        rw = int(random.uniform(0.12, 0.38) * w)
        rh = int(random.uniform(0.06, 0.16) * h)
        x = random.randint(0, max(0, w-rw))
        y = random.randint(0, max(0, h-rh))
        color = tuple(int(255*random.uniform(0.6,1.0)) for _ in range(3))
        draw.rectangle([x,y,x+rw,y+rh], fill=color)
        try:
            font = ImageFont.truetype("arial.ttf", max(12, int(h*0.03)))
        except:
            font = ImageFont.load_default()
        draw.text((x+5, y+5), "Sample", fill=(0,0,0), font=font)
    # final resize to target size
    img = img.resize(IMG_SIZE, Image.BILINEAR)
    return img

def process_one(src_path, start_idx):
    try:
        base = Image.open(src_path).convert("RGB")
    except Exception as e:
        print("Skipping (cannot open):", src_path, "->", e)
        return 0
    count = 0
    for i in range(N_PER_IMAGE):
        img = base.copy()
        img = random_edit(img)
        # occasionally add fake text overlay (brand misspelling)
        if random.random() < 0.3:
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except:
                font = ImageFont.load_default()
            draw.text((8, img.size[1]-26), "KYGESlC", fill=(150,20,20), font=font)
        # choose train or val
        if random.random() < VAL_RATIO:
            dst = os.path.join(OUT_VAL, f"fake_{start_idx+i:04d}.jpg")
        else:
            dst = os.path.join(OUT_TRAIN, f"fake_{start_idx+i:04d}.jpg")
        # save with JPEG compression
        img.save(dst, format="JPEG", quality=random.randint(55,92))
        count += 1
    return count

def main():
    # gather source images
    exts = (".jpg", ".jpeg", ".png", ".webp", ".bmp")
    files = [os.path.join(SRC_DIR, f) for f in os.listdir(SRC_DIR) if f.lower().endswith(exts)]
    if not files:
        print("No source images found in", SRC_DIR)
        return
    print("Found", len(files), "source images.")
    idx = 0
    for src in files:
        print("Processing:", src)
        created = process_one(src, idx)
        idx += created
    print("Done. Generated", idx, "fake images (train+val).")
    print("Train fake folder:", OUT_TRAIN)
    print("Val fake folder:", OUT_VAL)

if __name__ == "__main__":
    random.seed(42)
    main()
