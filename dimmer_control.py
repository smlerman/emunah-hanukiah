import json
import random
import time

import RPi.GPIO as GPIO

LIGHT_STATES = list()

LIGHT_MAP = {
    0: 3,
    1: 5,
    2: 7,
    3: 11,
    4: 13,
    5: 15,
    6: 19,
    7: 21,
    8: 23
}

ZERO_CROSS_COUNT = 0

def zero_cross_detect(channel):
    global ZERO_CROSS_COUNT
    ZERO_CROSS_COUNT += 1
    if ZERO_CROSS_COUNT < 2:
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
    

def read_light_state_file():
    fh = open("/var/www/html/menorah/light_states.txt")
    json_string = fh.read().strip()
    fh.close()
    
    new_light_states = json.loads(json_string)
    
    return new_light_states

LIGHT_STATES = read_light_state_file()

GPIO.setmode(GPIO.BOARD)
GPIO.setup(8, GPIO.IN)

for pin in LIGHT_MAP.values():
    GPIO.setup(pin, GPIO.OUT)

GPIO.add_event_detect(8, GPIO.RISING, callback=zero_cross_detect)

while True:
    time.sleep(1)
    LIGHT_STATES = read_light_state_file()
