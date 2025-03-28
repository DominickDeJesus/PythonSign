#!/bin/bash
#cd /home/pi/sign
#tmux new-session -d -s sign
#tmux send-key 'sudo python /home/pi/sign/led_display.py' C-m
tmux new -d -s sign-controller 'python /home/pi/sign/led_display.py'
tmux new -d -s sign-server 'python /home/pi/sign/server.py'
#cd ~
