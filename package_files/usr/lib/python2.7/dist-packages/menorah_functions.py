import json
import os

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

LIGHT_STATES_FILE_PATH = "/var/www/html/menorah/light_state/light_states.txt"

def read_light_state_file():
    # If the light states file doesn't exist, create it and set all lights to off
    if not os.path.exists(LIGHT_STATES_FILE_PATH):
        new_light_states = [False, False, False, False, False, False, False, False, False]
        write_light_state_file(new_light_states)
    
    fh = open(LIGHT_STATES_FILE_PATH)
    json_string = fh.read().strip()
    new_light_states = json.loads(json_string)
    
    fh.close()
    
    return new_light_states

def write_light_state_file(new_light_states):
    json_string = json.dumps(new_light_states)
    fh = open(LIGHT_STATES_FILE_PATH, "w")
    fh.write(json_string)
    fh.close()
 