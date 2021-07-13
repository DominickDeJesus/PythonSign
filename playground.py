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

#Globals
image_file_path = "/home/pi/assets/"
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
    "baby":"baby.gif",
    "trex":"trex.gif",
    'yoshi':'yoshi2.gif',
    'piano':'piano.gif'
}
fn = "logo"
last_fn = 'logo'
sched_on = True
cycle_on = True

def print_header():
    os.system("clear")
    global sched_on
    print("Press CTRL-C to stop.")
    print('Schedule: on' if sched_on else 'Schedule: off')
    print('Displaying: ' + fn)
    print('Cycle: ' + ('on' if cycle_on else 'off'))
    print("1-logo 2-thumbs up 3-meeting 4-onair 5-lucci 6-torch"
            +"\n7-pizza 8-kirby 9-toad 10-baby 11-trex 12-yoshi 13-piano")
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
        return 'baby'
    if key == '11':
        return 'trex'
    if key == '12':
        return 'yoshi'
    if key == '13':
        return 'piano'
    return "logo"

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

def showImage(img):
    global duration
    global image
    image = Image.open(image_file_path + images.get(img,"logo.png"))    
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
            else:
                showImage(fn)
except KeyboardInterrupt:
    sys.exit(0)
