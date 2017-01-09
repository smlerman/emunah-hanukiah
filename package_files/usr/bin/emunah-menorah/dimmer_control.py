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

FLICKER_TIME_FRACTION = 1.0/30.0
REGULAR_ON_TIME = 0.013333

ZERO_CROSS_COUNTER = 0

# Check for putting a light in "flicker" state once per second (120 ticks)
FLICKER_CHECK_COUNTER = 0

FLICKER_TICK_COUNT = [0, 0, 0, 0, 0, 0, 0, 0, 0]

def zero_cross_detect(channel):
    global ZERO_CROSS_COUNTER, FLICKER_CHECK_COUNTER
    ZERO_CROSS_COUNTER += 1
    FLICKER_CHECK_COUNTER += 1
    
    if ZERO_CROSS_COUNTER < ZERO_CROSS_COUNT_MAX:
        return
    
    ZERO_CROSS_COUNTER = 0
    
    # Check for putting a light in "flicker" state
    if FLICKER_CHECK_COUNTER >= 12:
        FLICKER_CHECK_COUNTER = 0
        
        for i in range(0,9):
            if LIGHT_STATES[i] and (FLICKER_TICK_COUNT[i] <= 0):
                flicker_check = random.random()
                if flicker_check < FLICKER_TIME_FRACTION:
                    # Set the light to flicker for a random number of ticks (120 ticks/second)
                    FLICKER_TICK_COUNT[i] = int(random.random() * 120) + 60
    
    # Get 9 random time lengths
    light_times = dict()
    
    for i in range(0,9):
        if LIGHT_STATES[i]:
            # Turn on the light
            GPIO.output(LIGHT_MAP[i], GPIO.HIGH)
            
            if FLICKER_TICK_COUNT[i] > 0:
                # Most of the function is executed every other tick, so subtract 2 ticks from the counter
                FLICKER_TICK_COUNT[i] -= 2
                
                # Full time for this is 0.01666 seconds
                #random_time = random.uniform(0.002777, 0.008333)
                random_time = random.uniform(0.005555, 0.016666)
            else:
                random_time = REGULAR_ON_TIME
            
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
    
# Handle SIGQUIT, sent by systemctl stop
def sigquit_handler(a, b):
    board_cleanup()
    sys.exit(0)

# Handle SIGHUP, sent by systemctl reload
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
