#!/bin/bash

# Wait for system to fully boot
sleep 2

# Start LED controller in tmux
tmux new-session -d -s controller 'python3 /home/pi/sign/led_display.py'

# Start Flask server in tmux
tmux new-session -d -s server 'python3 /home/pi/sign/server.py'
