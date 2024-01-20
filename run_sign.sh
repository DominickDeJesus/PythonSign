#!/bin/bash
#cd /home/pi/sign
#tmux new-session -d -s sign
#tmux send-key 'sudo python /home/pi/sign/playground.py' C-m
tmux new -d -s sign 'python /home/pi/sign/playground.py'
#cd ~
