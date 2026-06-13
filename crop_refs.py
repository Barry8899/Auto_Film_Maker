from PIL import Image
import os

def crop_right_part(img_path, out_path, crop_ratio=0.28):
    with Image.open(img_path) as im:
        width, height = im.size
        left = int(width * crop_ratio)
        top = 0
        right = width
        bottom = height
        im_cropped = im.crop((left, top, right, bottom))
        im_cropped.save(out_path)
        print(f"Cropped {img_path} -> {out_path} with ratio {crop_ratio}")

base_dir = "/home/admin/.openclaw/workspace/auto_film_maker/repo/S6_Video_Generation/stark_and_dad/Shot_06/refs/"
crop_right_part(os.path.join(base_dir, "stark_106_2.jpg"), os.path.join(base_dir, "stark_106_2_cropped.jpg"), 0.28)
crop_right_part(os.path.join(base_dir, "howard_1_4.jpg"), os.path.join(base_dir, "howard_1_4_cropped.jpg"), 0.28)
