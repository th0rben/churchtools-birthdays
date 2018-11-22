#!/bin/bash
cd /home/pi/git/churchtools-birthdays #change to your directory
git pull
echo "Last pull: $(date)" >> cron.log
python3 churchtools_birthdays.py
