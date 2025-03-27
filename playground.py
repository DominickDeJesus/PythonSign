import time
import os
import json
import random
import datetime
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageSequence

# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 32
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat-pwm'
options.drop_privileges = False

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
themes_dir = os.path.join(BASE_DIR, "themes")
assets_dir = os.path.join(BASE_DIR, "themes/all")
settings_file = os.path.join(BASE_DIR, "settings.json")

matrix = RGBMatrix(options=options)

def load_settings():
    try:
        with open(settings_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "mode": "logo", 
            "theme": None, 
            "duration": 2,
            "sleep_enable": True, 
            "sleep_range": {"start": "00:00", "end": "09:00"}
        }

def get_theme_images(theme):
    theme_path = os.path.join(themes_dir, theme)
    if not os.path.isdir(theme_path):
        return []
    return [os.path.join(theme_path, f) for f in os.listdir(theme_path) if f.lower().endswith(('.png', '.jpg', '.gif'))]

def show_image(image_path, duration):
    image = Image.open(image_path)
    image.thumbnail((matrix.width, matrix.height), Image.ANTIALIAS)
    frame_duration = image.info.get("duration", 0) / 1000.0

    if frame_duration == 0:
        matrix.SetImage(image.convert("RGB"))
        time.sleep(duration)
    else:
        for frame in ImageSequence.Iterator(image):
            matrix.SetImage(frame.convert("RGB"))
            time.sleep(frame_duration if frame_duration > 0 else 0.1)

def is_sleep_time(schedule_on, sleep_range):
    if not schedule_on:
        return False

    now = datetime.datetime.now().time()

    start_str = sleep_range.get("start", "00:00")
    end_str = sleep_range.get("end", "09:00")

    try:
        start = datetime.datetime.strptime(start_str, "%H:%M").time()
        end = datetime.datetime.strptime(end_str, "%H:%M").time()
    except ValueError:
        return False  # fallback if settings are corrupted

    if start < end:
        return start <= now < end
    else:
        return now >= start or now < end
    

if __name__ == "__main__":
    while True:
        settings = load_settings()
        mode = settings.get("mode", "all")
        theme = settings.get("theme", None)
        duration = settings.get("duration", 60)
        sleep_enable = settings.get("sleep_enable", True)
        sleep_range = settings.get("sleep_range", {"start": "00:00", "end": "09:00"})

        if is_sleep_time(sleep_enable, sleep_range):
            images = get_theme_images('sleep')
            if images:
                random.shuffle(images)
                for img in images:
                    show_image(img, duration)
        elif theme:
            images = get_theme_images(theme)
            if images:
                random.shuffle(images)
                for img in images:
                    show_image(img, duration)
        else:
            logo_path = os.path.join(assets_dir, "logo.png")
            show_image(logo_path, duration)

        time.sleep(0.1)
