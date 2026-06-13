from PIL import Image
import os

img_path = "/home/admin/.openclaw/workspace/auto_film_maker/repo/S6_Video_Generation/stark_and_dad/Shot_06/refs/new_tony_ref.jpg"
out_path = "/home/admin/.openclaw/workspace/auto_film_maker/repo/S6_Video_Generation/stark_and_dad/Shot_06/refs/new_tony_ref_cropped.jpg"

with Image.open(img_path) as im:
    width, height = im.size
    # Keep the left part, remove the right back silhouette
    # Let's keep the left 60% of the image
    right = int(width * 0.60)
    im_cropped = im.crop((0, 0, right, height))
    im_cropped.save(out_path)
    print(f"Cropped {img_path} -> {out_path} (kept left 60%)")
