import json
import random
import time

import RPi.GPIO as GPIO

LIGHT_STATES = list()

LIGHT_MAP = {
    0: 3,
    1: 5,
    2: 7,
    3: 11
}

def zero_cross_detect(channel):
    # Get 9 random time lengths
    light_times = dict()
    
    for i in range(0,4):
        if LIGHT_STATES[i]:
            # Turn on the light
            GPIO.output(LIGHT_MAP[i], GPIO.HIGH)
            
            #random_time = random.randint(0,1)
            random_time = random.uniform(0.002, 0.008333)
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
    new_light_states = [False, False, False, False, False, False, False, False, False]
    
    fh = open("/var/www/html/menorah/light_states.txt")
    # json_string = fh.read().strip()
    # new_light_states = json.loads(json_string)
    for line in fh:
        try:
            light_on = int(line.strip())
            new_light_states[light_on] = True
        except ValueError:
            pass
    
    fh.close()
    
    return new_light_states

LIGHT_STATES = read_light_state_file()

GPIO.setmode(GPIO.BOARD)
GPIO.setup(26, GPIO.IN)

GPIO.setup(3, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(7, GPIO.OUT)
GPIO.setup(11, GPIO.OUT)

#GPIO.add_event_detect(26, GPIO.RISING, callback=zero_cross_detect)

while True:
    time.sleep(1.0/60)
    LIGHT_STATES = read_light_state_file()
    zero_cross_detect(26)
