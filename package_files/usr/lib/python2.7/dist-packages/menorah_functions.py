import datetime
import json
import os
import subprocess

import hdate
import RPi.GPIO as GPIO

# Dictionary of light number => GPIO pin
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

LIGHT_STATES_FILE_PATH = "/var/www/emunah-menorah/light_state/light_states.txt"

def read_light_state_file():
    # If the light states file exists, read the light states from it, otherwise create it and set all lights to off
    if os.path.exists(LIGHT_STATES_FILE_PATH):
        fh = open(LIGHT_STATES_FILE_PATH)
        json_string = fh.read().strip()
        fh.close()
        
        new_light_states = json.loads(json_string)
    else:
        new_light_states = [False, False, False, False, False, False, False, False, False]
        write_light_state_file(new_light_states)
    
    return new_light_states

def write_light_state_file(new_light_states):
    json_string = json.dumps(new_light_states)
    fh = open(LIGHT_STATES_FILE_PATH, "w")
    fh.write(json_string)
    fh.close()

def turn_on_light(light_number):
    # Get the current light states
    current_light_states = read_light_state_file()
    
    current_light_states[light_number] = True
    
    # Output the new states
    write_light_state_file(current_light_states)
    
    # Send a reload command to the service
    reload_service()
    
def turn_off_light(light_number):
    # Get the current light states
    current_light_states = read_light_state_file()
    
    current_light_states[light_number] = False
    
    # Output the new states
    write_light_state_file(current_light_states)
    
    # Send a reload command to the service
    reload_service()
    
def get_current_day(current_datetime = None):
    if current_datetime is None:
        current_datetime = datetime.datetime.now()
    
    current_date = current_datetime.date()
    
    current_hdate = hdate.Hdate()
    current_hdate.set_gdate(current_date.day, current_date.month, current_date.year)
    current_hdate.set_location(42.420758, -71.227494, -5)
    
    # Use 1 hour before sunset
    sunset_timedelta = datetime.timedelta(minutes=current_hdate.get_sunset() - 60)
    sunset_datetime = datetime.datetime.combine(current_date, datetime.time()) + sunset_timedelta
    
    if current_datetime >= sunset_datetime:
        current_date = current_date + datetime.timedelta(1)
    
    hdate_first_hanukah = hdate.Hdate()
    hdate_first_hanukah.set_gdate(current_date.day, current_date.month, current_date.year)
    # First candle is the night following 24 Kislev
    hdate_first_hanukah.set_hdate(24, 3, hdate_first_hanukah.get_hyear())
    
    date_first_hanukah = datetime.date(hdate_first_hanukah.get_gyear(), hdate_first_hanukah.get_gmonth(), hdate_first_hanukah.get_gday())
    
    current_day_timedelta = current_date - date_first_hanukah
    current_day = current_day_timedelta.days
    
    return current_day

def turn_on_next_light(use_current_day = False):
    # Get the current light states
    current_light_states = read_light_state_file()
    
    # Find the first light that's off and turn it on
    next_light_found = False
    
    if use_current_day:
        # Count down from the current day to 0
        current_day = get_current_day()
        candle_list = [0] + list(range(current_day, 0, -1))
    else:
        candle_list = range(0, len(current_light_states))
    
    for candle in candle_list:
        if current_light_states[candle] == False:
            current_light_states[candle] = True
            next_light_found = True
            break
    
    # If all of the lights are on, turn them all off
    if not next_light_found:
        current_light_states = new_light_states = [False, False, False, False, False, False, False, False, False]
    
    # Output the new states
    write_light_state_file(current_light_states)
    
    # Send a reload command to the service
    reload_service()

def board_cleanup():
    GPIO.setmode(GPIO.BOARD)
    
    # Turn off all of the lights
    for pin in LIGHT_MAP.values():
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)

    GPIO.cleanup()

def restart_service():
    subprocess.check_call(["sudo", "/bin/systemctl", "restart", "emunah-menorah"])

def stop_service():
    subprocess.check_call(["sudo", "/bin/systemctl", "stop", "emunah-menorah"])

def reload_service():
    subprocess.check_call(["sudo", "/bin/systemctl", "reload", "emunah-menorah"])
