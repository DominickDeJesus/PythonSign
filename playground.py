#!/usr/bin/env python
import time
import datetime
import sys
import select
import os
from rgbmatrix import RGBMatrix, RGBMatrixOptions
import threading
from PIL import Image
from PIL import ImageSequence

# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 32
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat-pwm'  # If you have an Adafruit HAT: 'adafruit-hat'
# options.pwm_bits = 1
options.drop_privileges = False

<<<<<<< Updated upstream
#Globals
image_file_path = "/home/pi/sign/assets/"
matrix = RGBMatrix(options = options)
image = Image.open(image_file_path + "logo.png")    
image.thumbnail((matrix.width, matrix.height), Image.ANTIALIAS)
duration = image.info.get("duration", 0) / 1000.0
matrix.SetImage(image.convert('RGB'))
images = {
    "thumbsup":"thumbsup.png",
    "meeting":"meeting.gif",
    "onair":"onair.gif",
    "kirby":"kirby.gif",
    "logo":"logo.png",
    "fire":"torch2.gif",
    "lucci":"lucci.jpg",
    "pizza":"pizza.gif",
    "toad":"toad.gif",
    "lego":"lego_logo.gif",
    "trex":"trex.gif",
    'yoshi':'yoshi2.gif',
    'piano':'piano.gif',
    "turkey-fly": "turkey-fly.gif",
    "turkey-run": "turkey-run.gif",
    "turkey-plate": "turkey-plate.jpg",
    "christmas-tree-snow": "christmas-tree-snow.gif",
    "elf-dance": "elf-dance.gif",
    "santa-dance": "santa-dance.gif"
}

christmas_images_array = [
        "christmas-tree-snow",
        "elf-dance",
        "santa-dance"
        ]

fn = "logo"
last_fn = 'logo'
sched_on = True
cycle_on = True
turkey_time_on = False
christmas_time_on = False

def print_header():
    os.system("clear")
    global sched_on
    print("Press CTRL-C to stop.")
    print('Schedule: on' if sched_on else 'Schedule: off')
    print('Displaying: ' + fn)
    print('Cycle: ' + ('on' if cycle_on else 'off'))
    print('Christmas: ' + ('on' if christmas_time_on else 'off'))
    print("1-logo 2-thumbs up 3-meeting 4-onair 5-lucci 6-torch"
            +"\n7-pizza 8-kirby 9-toad 10-lego 11-trex 12-yoshi 13-piano 17-christmas")
    print('s-toggle scheduler c-toggle cycle')    

def getTheImageName(key):
    if key == '1':
        return "logo"
    if key == '2':
        return "thumbsup"
    if key == '3':
        return "meeting"
    if key == '4':
        return "onair"
    if key == '5':
        return "lucci"
    if key == '6':
        return 'fire'
    if key == '7':
        return "pizza"
    if key == '8':
        return "kirby"
    if key == '9':
        return 'toad'
    if key == '10':
        return 'lego'
    if key == '11':
        return 'trex'
    if key == '12':
        return 'yoshi'
    if key == '13':
        return 'piano'
    if key == '14':
        return 'turkey-fly'
    if key == '15':
        return 'turkey-plate'
    if key == '16':
        return 'turkey-run'
    if key == '17':
        return 'christmas-tree-snow'
    if key == '18':
        return 'elf-dance'
    if key == '19':
        return 'santa-dance'
    return "logo"

def getChristmasImage():
    num = (datetime.datetime.now().time().minute // 20)
    print(num)
    return christmas_images_array[num]

class KeyboardThread(threading.Thread):
    def __init__(self, input_cbk = None, name='keyboard-input-thread'):
        self.input_cbk = input_cbk
        super(KeyboardThread, self).__init__(name=name)
        self.start()

        def run(self):
            while True:
                self.input_cbk(input()) #waits to get input + Return

def is_sleep_time(scheduleOn):
    if not scheduleOn:
        return False
    hour = datetime.datetime.now().time().hour
    if 0 <= hour and hour < 9:
        return True
    return False

def is_cycle_time(cycle):
    hour = datetime.datetime.now().time().hour
    if not cycle:
        return False
    if 9 < hour and hour < 23:
        return True
    return False

def is_turkey_time():
    num = (datetime.datetime.now().time().hour % 3) + 14
    return

def showImage(img):
    global duration
    global image
    image = Image.open(image_file_path + images.get(img,"logo.png"))    
=======
# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
themes_dir = os.path.join(BASE_DIR, "themes")
settings_file = os.path.join(BASE_DIR, "settings.json")

matrix = RGBMatrix(options=options)


def load_settings():
    """Load settings from JSON file."""
    try:
        with open(settings_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"mode": "all", "theme": None, "duration": 60, "sleep_enable": False, "sleep_start": "19:00:00", "sleep_end": "06:00:00"}


def get_theme_images(theme):
    """Get all image files in the selected theme folder."""
    theme_path = os.path.join(themes_dir, theme)
    if not os.path.isdir(theme_path):
        return []

    return [
        os.path.join(theme_path, f)
        for f in os.listdir(theme_path)
        if f.lower().endswith((".png", ".jpg", ".gif"))
    ]


def show_image(image_path, duration):
    """Display an image or animated GIF on the LED matrix."""
    image = Image.open(image_path)
>>>>>>> Stashed changes
    image.thumbnail((matrix.width, matrix.height), Image.ANTIALIAS)
    duration = image.info.get("duration", 0) / 1000.0
    if duration == 0:
        matrix.SetImage(image.convert("RGB"))
    else:
        for frame in ImageSequence.Iterator(image):
            matrix.SetImage(frame.convert("RGB"))
            time.sleep(duration)


#Main section to run
try:
    print_header()
    while True:
<<<<<<< Updated upstream
        inp = select.select([sys.stdin],[],[],0)[0]
        if inp:
            value = sys.stdin.readline().rstrip()
            if (value == "q"):
                print "Exiting"
                sys.exit(0)
            elif value == 's':
                sched_on = not sched_on
                print_header()
            elif value == 'c':
                cycle_on = not cycle_on
                print_header()
            elif value == 't':
                turkey_time_on = not turkey_time_on
                print_header()
            elif value == 'h':
                christmas_time_on = not christmas_time_on
                print_header()
            else:
                cycle_on = False
                fn = getTheImageName(value)
                showImage(fn)
                print_header()
        else:
            if is_sleep_time(sched_on):
                cycle_on = True
                fn = 'fire'
                showImage(fn)
            elif is_cycle_time(cycle_on):
                num = (datetime.datetime.now().time().hour % 5) + 8
                fn = getTheImageName(str(num))
                showImage(fn)
            elif turkey_time_on:
                num = (datetime.datetime.now().time().hour % 3) + 14
                fn = getTheImageName(str(num))
                showImage(fn)
            elif christmas_time_on:
                fn = getChristmasImage()
                showImage(fn)
            else:
                showImage(fn)
except KeyboardInterrupt:
    sys.exit(0)
=======
        settings = load_settings()
        mode = settings.get("mode", "all")
        theme = settings.get("theme", None)
        duration = settings.get("duration", 60)
        sleep_enable = settings.get("sleep_enable", False)
        sleep_start = settings.get("sleep_start", "19:00:00")
        sleep_end = settings.get("sleep_end", "06:00:00")

        if theme:
            images = get_theme_images(theme)
            if images:
                random.shuffle(images)  # Shuffle for variety
                for img in images:
                    show_image(img, duration)
        else:
            show_image(os.path.join(BASE_DIR, "all", "logo.png"), duration)

        time.sleep(0.1)  # Check for updates every 100ms
>>>>>>> Stashed changes
