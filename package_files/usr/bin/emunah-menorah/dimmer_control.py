#!/usr/bin/python3

import random
import signal
import sys
import time

import RPi.GPIO as GPIO

from menorah_functions import *

LIGHT_STATES = list()

PERIODS_PER_SECOND = 60
ZERO_CROSS_COUNT_MAX = (120 / PERIODS_PER_SECOND)

ZERO_CROSS_COUNT = 0

def zero_cross_detect(channel):
    global ZERO_CROSS_COUNT
    ZERO_CROSS_COUNT += 1
    if ZERO_CROSS_COUNT < ZERO_CROSS_COUNT_MAX:
        return
    
    ZERO_CROSS_COUNT = 0
    
    # Get 9 random time lengths
    light_times = dict()
    
    for i in range(0,9):
        if LIGHT_STATES[i]:
            # Turn on the light
            GPIO.output(LIGHT_MAP[i], GPIO.HIGH)
            
            full_or_partial_time = random.randint(0,1)
            if full_or_partial_time == 0:
                random_time = random.uniform(0.002777, 0.008333)
                if random_time not in light_times:
                    light_times[random_time] = list()
                
                light_times[random_time].append(i)
        else:
            GPIO.output(LIGHT_MAP[i], GPIO.LOW)
    
    light_times_list = sorted(light_times.keys())
    
    for i in range(0, len(light_times_list)):
        if i == 0:
            light_time = light_times_list[i]
        else:
            light_time = light_times_list[i] - light_times_list[i - 1]
        
        time.sleep(light_time)
        
        for light in light_times[light_times_list[i]]:
            GPIO.output(LIGHT_MAP[light], GPIO.LOW)
    
def sigquit_handler(a, b):
    board_cleanup()
    sys.exit(0)

def sighup_handler(a, b):
    global LIGHT_STATES
    LIGHT_STATES = read_light_state_file()

LIGHT_STATES = read_light_state_file()

GPIO.setmode(GPIO.BOARD)
GPIO.setup(8, GPIO.IN)

for pin in LIGHT_MAP.values():
    GPIO.setup(pin, GPIO.OUT)

GPIO.add_event_detect(8, GPIO.RISING, callback=zero_cross_detect)

signal.signal(signal.SIGQUIT, sigquit_handler)
signal.signal(signal.SIGHUP, sighup_handler)

while True:
    time.sleep(30)
    LIGHT_STATES = read_light_state_file()
