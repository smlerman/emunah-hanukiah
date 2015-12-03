#!/usr/bin/python

import sys

import RPi.GPIO as GPIO

pin_number = int(sys.argv[1])

GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin_number, GPIO.OUT)

current_state = GPIO.input(pin_number)

print(current_state)
