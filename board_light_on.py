#!/usr/bin/python

import sys

import RPi.GPIO as GPIO

pin_number = int(sys.argv[1])

GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin_number, GPIO.OUT)
GPIO.output(pin_number, GPIO.HIGH)
