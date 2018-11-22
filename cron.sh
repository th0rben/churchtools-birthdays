#!/bin/bash
cd /home/pi/git/churchtools-birthdays #change to your directory
git pull
echo "Last pull: $(date)" >> cron.log
cd src
python3 main.py
