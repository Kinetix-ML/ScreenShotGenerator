import os
import shutil
from PIL import Image, ImageDraw, ImageFont
from os import walk, path
import json


def screenshot_to_device(offset, device, screenshot):
    img = Image.new('RGBA', device.size, (0, 0, 0, 0))
    img.paste(screenshot, offset)
    img.paste(device, (0,0), device)
    return img


def device_to_background(offset, size, device, background):
    background = background.resize(size)
    w = background.size[0]-offset[0]*2
    h = device.size[1]/device.size[0]*w
    device = device.resize((int(w),int(h)))
    top_offset = size[1]-device.size[1]-offset[1]
    background.paste(device, (offset[0], top_offset), device)
    return background


def text_to_background(background, text, font, text_color, top):
    W, H = background.size
    draw = ImageDraw.Draw(background)
    _, _, w, h = draw.textbbox((0, 0), text, font=font, align="center")
    draw.text(((W - w) / 2, top), text, font=font, fill=text_color, align="center")
    return background


def generate_for_device(dir, export):
    device = Image.open(path.join(dir, "device.png"))
    os.mkdir(export)
    screenshots = []
    backgrounds = []
    for (dirpath, dirnames, filenames) in walk(path.join(dir, "Screenshots")):
        screenshots.extend(filenames)
        screenshots.sort()
        break
    for (dirpath, dirnames, filenames) in walk(path.join(dir, "Backgrounds")):
        backgrounds.extend(filenames)
        backgrounds.sort()
        break

    f = open(path.join(dir, "cfg.json"), "r")
    s = f.read()
    cfg = json.loads(s)
    screenshot_offset = (cfg["screenshot"]["offset_x"], cfg["screenshot"]["offset_y"])
    device_offset = (cfg["background"]["offset_x"], cfg["background"]["offset_y"])
    top = cfg["text"]["top"]
    font = cfg["text"]["font"]
    font_size = cfg["text"]["size"]
    labels = cfg["labels"]
    width = cfg["width"]
    height = cfg["height"]

    print(f"Generating {len(screenshots)}")

    for (i, screenshot_path) in enumerate(screenshots):
        print(f"[{i+1}/{len(screenshots)}] Generating Screenshot")
        screenshot = Image.open(path.join(dir, "Screenshots", screenshot_path))
        background = Image.open(path.join(dir, "Backgrounds", backgrounds[i])).convert("RGB")
        screenshot_on_device = screenshot_to_device(screenshot_offset, device, screenshot)
        device_on_background = device_to_background(device_offset, (width,height), screenshot_on_device, background)
        with_text = text_to_background(device_on_background, labels[i], ImageFont.truetype(font, size=font_size), (255,255,255),top)
        with_text.save(path.join(export, str(i+1)+".jpg"))


if __name__ == "__main__":
    assets = "Assets"
    export = "Export"
    try:
        os.mkdir(export)
    except:
        print("Export Directory Already Exists. ")
        if input(f"Delete export directory ({export}) and continue? (y/N) ") == "y":
            shutil.rmtree(export)
            os.mkdir(export)

    devices = []
    for (dirpath, dirnames, filenames) in walk(assets):
        devices.extend(dirnames)
        break

    print(f"Generating for {len(devices)} devices")

    for (i, device) in enumerate(devices):
        print(f"[{i+1}/{len(devices)}] Device {device}")
        generate_for_device(path.join(assets, device), path.join(export, device))
