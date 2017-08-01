#!/usr/bin/python3

import random
import signal
import sys
import time

import RPi.GPIO as GPIO

from menorah_functions import *

# List of current states for each light
LIGHT_STATES = list()

# Set lights to flicker on every other zero cross
ZERO_CROSS_COUNTER = 0
ZERO_CROSS_COUNT_MAX = 2

# Values to control how the lights flicker
FLICKER_TIME_FRACTION = 1.0/20.0
REGULAR_ON_TIME = 0.015

# Check for putting a light in "flicker" state every 1/10 of a second (12 ticks)
FLICKER_CHECK_COUNTER = 0
FLICKER_CHECK_MAX = 12
FLICKER_TICK_COUNT = [0, 0, 0, 0, 0, 0, 0, 0, 0]

# Function that is called whenever a signal is received on the input pin
def zero_cross_detect(channel):
    global ZERO_CROSS_COUNTER, FLICKER_CHECK_COUNTER
    ZERO_CROSS_COUNTER += 1
    FLICKER_CHECK_COUNTER += 1
    
    # Skip the flicker code if the number of zero crosses hasn't reached the right total (default is every other zero cross)
    if ZERO_CROSS_COUNTER < ZERO_CROSS_COUNT_MAX:
        return
    
    ZERO_CROSS_COUNTER = 0
    
    # Check for putting a light in "flicker" state
    if FLICKER_CHECK_COUNTER >= FLICKER_CHECK_MAX:
        FLICKER_CHECK_COUNTER = 0
        
        for i in range(0,9):
            if LIGHT_STATES[i] and (FLICKER_TICK_COUNT[i] <= 0):
                flicker_check = random.random()
                if flicker_check < FLICKER_TIME_FRACTION:
                    # Set the light to flicker for a random number of ticks (120 ticks/second)
                    FLICKER_TICK_COUNT[i] = int(random.random() * 120) + 60
    
    # Get 9 random time lengths
    # It's highly improbable that more than one light will get the same random duration, but in case it does happen, this is a dictionary of duration => list of lights
    light_times = dict()
    
    for i in range(0,9):
        if LIGHT_STATES[i]:
            # Turn on the light
            GPIO.output(LIGHT_MAP[i], GPIO.HIGH)
            
            if FLICKER_TICK_COUNT[i] > 0:
                # Most of the function is executed every other tick, so subtract 2 ticks from the counter
                FLICKER_TICK_COUNT[i] -= 2
                
                # Full time for this is 0.01666 seconds
                random_time = random.uniform(0.005555, 0.016666)
            else:
                random_time = REGULAR_ON_TIME
            
            if random_time not in light_times:
                light_times[random_time] = list()
            
            light_times[random_time].append(i)
        
        else:
            # Turn off the light
            GPIO.output(LIGHT_MAP[i], GPIO.LOW)
    
    # Create a list of durations of the lights, sorted from least to greatest
    light_times_list = sorted(light_times.keys())
    
    for i in range(0, len(light_times_list)):
        # The first time period is the first duration
        if i == 0:
            light_time = light_times_list[i]
        # Each subsequent time period is the difference between this duration and the previous duration
        else:
            light_time = light_times_list[i] - light_times_list[i - 1]
        
        # Wait for the next duration to expire
        time.sleep(light_time)
        
        # Turn off each light that was randomly given the duration
        for light in light_times[light_times_list[i]]:
            GPIO.output(LIGHT_MAP[light], GPIO.LOW)
    
# Handle SIGQUIT, sent by systemctl stop
def sigquit_handler(signum, stack_frame):
    board_cleanup()
    sys.exit(0)

# Handle SIGHUP, sent by systemctl reload
def sighup_handler(signum, stack_frame):
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

# Read the light state file every 30 seconds, in case it was edited outside of the web page
while True:
    time.sleep(30)
    LIGHT_STATES = read_light_state_file()
