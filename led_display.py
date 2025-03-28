import os
import time
import json
import random
import datetime
from threading import Thread
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageSequence

# --- Matrix configuration ---
options = RGBMatrixOptions()
options.rows = 32
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat-pwm'
options.drop_privileges = False
matrix = RGBMatrix(options=options)

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
themes_dir = os.path.join(BASE_DIR, "themes")
settings_file = os.path.join(BASE_DIR, "settings.json")

# --- Shared settings ---
current_settings = {}

# --- Load settings safely ---
def load_settings():
    try:
        with open(settings_file, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[WARN] Failed to load settings.json: {e}")
        return {
            "mode": "all",
            "theme": "all",
            "duration": 2,
            "sleep_enable": False,
            "sleep_range": {"start": "00:00", "end": "09:00"},
            "static_image": "logo.png"
        }

# --- Watchdog handler ---
class SettingsChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith("settings.json"):
            time.sleep(0.1)
            global current_settings
            current_settings = load_settings()
            print(f"[WATCHDOG] settings.json reloaded at {datetime.datetime.now()}")

def start_settings_watcher():
    observer = Observer()
    event_handler = SettingsChangeHandler()
    observer.schedule(event_handler, path=BASE_DIR, recursive=False)
    observer.start()
    print("[WATCHDOG] Monitoring settings.json for changes")
    return observer

# --- Sleep time check ---
def is_sleep_time(enabled, sleep_range):
    if not enabled:
        return False
    now = datetime.datetime.now().time()
    try:
        start = datetime.datetime.strptime(sleep_range["start"], "%H:%M").time()
        end = datetime.datetime.strptime(sleep_range["end"], "%H:%M").time()
    except (KeyError, ValueError):
        print("[ERROR] Invalid sleep_range format")
        return False
    if start < end:
        return start <= now < end
    else:
        return now >= start or now < end

# --- Load images from theme ---
def get_theme_images(theme):
    theme_path = os.path.join(themes_dir, theme)
    if not os.path.isdir(theme_path):
        return []
    return [
        os.path.join(theme_path, f)
        for f in os.listdir(theme_path)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))
    ]

# --- Display image safely ---
def show_image(image_path, duration, allow_interrupt=True):
    try:
        image = Image.open(image_path)
        image.thumbnail((matrix.width, matrix.height), Image.ANTIALIAS)

        frame_duration = image.info.get("duration", 0) / 1000.0
        active_settings = current_settings.copy()

        if frame_duration == 0 or not getattr(image, "is_animated", False):
            matrix.SetImage(image.convert("RGB"))
            start = time.time()
            while time.time() - start < duration:
                if allow_interrupt and current_settings != active_settings:
                    print("[INFO] Settings changed mid-static image. Interrupting.")
                    return
                time.sleep(0.1)
        else:
            start_time = time.time()
            frames = [frame.copy() for frame in ImageSequence.Iterator(image)]
            while time.time() - start_time < duration:
                for frame in frames:
                    matrix.SetImage(frame.convert("RGB"))
                    time.sleep(frame_duration if frame_duration > 0 else 0.1)
                    if time.time() - start_time >= duration:
                        break
                    if allow_interrupt and current_settings != active_settings:
                        print("[INFO] Settings changed mid-GIF. Interrupting.")
                        return
    except Exception as e:
        print(f"[ERROR] Failed to show image {image_path}: {e}")

# --- Main loop ---
if __name__ == "__main__":
    print("🟢 LED Controller started with Watchdog")
    current_settings = load_settings()
    observer = start_settings_watcher()

    was_sleeping = False

    try:
        while True:
            theme = current_settings.get("theme", "all")
            duration = current_settings.get("duration", 2)
            sleep_enabled = current_settings.get("sleep_enable", False)
            sleep_range = current_settings.get("sleep_range", {"start": "00:00", "end": "09:00"})
            static_image = current_settings.get("static_image")

            sleeping = is_sleep_time(sleep_enabled, sleep_range)

            if sleeping:
                if not was_sleeping:
                    print("[MODE] Entering Sleep Mode")
                    was_sleeping = True

                sleep_images = get_theme_images("sleep")
                if sleep_images:
                    random.shuffle(sleep_images)
                    for img in sleep_images:
                        show_image(img, duration, allow_interrupt=False)
                        if not is_sleep_time(current_settings.get("sleep_enable"), current_settings.get("sleep_range", {})):
                            print("[MODE] Exiting Sleep Mode")
                            was_sleeping = False
                            break
                else:
                    print("[MODE] Sleep fallback → logo")
                    show_image(os.path.join(themes_dir, "all", "logo.png"), duration, allow_interrupt=False)
                continue

            was_sleeping = False

            if static_image and theme:
                image_path = os.path.join(themes_dir, theme, static_image)
                if os.path.exists(image_path):
                    print(f"[MODE] Static Image: {static_image}")
                    show_image(image_path, duration)
                    continue

            if theme:
                images = get_theme_images(theme)
                if images:
                    print(f"[MODE] Cycling Theme: {theme} ({len(images)} images)")
                    random.shuffle(images)
                    for img in images:
                        show_image(img, duration)
                        if current_settings.get("theme") != theme:
                            break
                    continue

            print("[MODE] Default → logo")
            show_image(os.path.join(themes_dir, "all", "logo.png"), duration)

    except KeyboardInterrupt:
        print("\n🛑 Shutting down LED controller")
        observer.stop()
        observer.join()