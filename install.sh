#!/bin/sh

sudo mkdir /usr/local/lib/marax-temp-display/
sudo cp ./temp_display.py /usr/local/lib/marax-temp-display/
sudo chown root:root /usr/local/lib/marax-temp-display/temp_display.py
sudo chmod 644 /usr/local/lib/marax-temp-display/temp_display.py

sudo cp ./marax-temp-display.service /etc/systemd/system/
sudo chown root:root /etc/systemd/system/marax-temp-display.service
sudo chmod 644 /etc/systemd/system/marax-temp-display.service

sudo systemctl enable marax-temp-display