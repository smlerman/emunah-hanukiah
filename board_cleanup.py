#!/usr/bin/python

import RPi.GPIO as GPIO

from menorah_functions import *

GPIO.setmode(GPIO.BOARD)

for pin in LIGHT_MAP.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

GPIO.cleanup()
