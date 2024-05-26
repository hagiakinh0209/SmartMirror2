#!/bin/bash

# Uninstall the virtual microphone.

pactl unload-module module-pipe-source
rm /home/kinh/.config/pulse/client.conf