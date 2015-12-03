import subprocess
import urlparse

#import RPi.GPIO as GPIO

HTML_TEMPLATE = """
<html>
<head>
    <style>
        .light_row {{
            height: 60px;
        }}
        .light_width {{
            width: 10%;
        }}
        
        .shamesh_width {{
            width: 20%;
        }}
        
        .light-unlit {{
            color: #FFFFFF;
            background-color: #000000;
        }}
        
        .light-lit {{
            color: #FF0000;
            background-color: #FFFF00;
        }}
    </style>
</head>
<body>
    <table width="100%">
        <tr class="light_row">
            <td class="light_width {light_state_8}">8</td>
            <td class="light_width {light_state_7}">7</td>
            <td class="light_width {light_state_6}">6</td>
            <td class="light_width {light_state_5}">5</td>
            <td class="shamesh_width {light_state_0}">0</td>
            <td class="light_width {light_state_4}">4</td>
            <td class="light_width {light_state_3}">3</td>
            <td class="light_width {light_state_2}">2</td>
            <td class="light_width {light_state_1}">1</td>
        </tr>
        <tr class="light_row">
            <td>
                <a href="/menorah?candle=8&action=1">ON</a>
            </td>
            <td>
                <a href="/menorah?candle=7&action=1">ON</a>
            </td>
            <td>
                <a href="/menorah?candle=6&action=1">ON</a>
            </td>
            <td>
                <a href="/menorah?candle=5&action=1">ON</a>
            </td>
            <td>
                <a href="/menorah?candle=0&action=1">ON</a>
            </td>
            <td>
                <a href="/menorah?candle=4&action=1">ON</a>
            </td>
            <td>
                <a href="/menorah?candle=3&action=1">ON</a>
            </td>
            <td>
                <a href="/menorah?candle=2&action=1">ON</a>
            </td>
            <td>
                <a href="/menorah?candle=1&action=1">ON</a>
            </td>
        </tr>
        <tr class="light_row">
            <td>
                <a href="/menorah?candle=8&action=0">OFF</a>
            </td>
            <td>
                <a href="/menorah?candle=7&action=0">OFF</a>
            </td>
            <td>
                <a href="/menorah?candle=6&action=0">OFF</a>
            </td>
            <td>
                <a href="/menorah?candle=5&action=0">OFF</a>
            </td>
            <td>
                <a href="/menorah?candle=0&action=0">OFF</a>
            </td>
            <td>
                <a href="/menorah?candle=4&action=0">OFF</a>
            </td>
            <td>
                <a href="/menorah?candle=3&action=0">OFF</a>
            </td>
            <td>
                <a href="/menorah?candle=2&action=0">OFF</a>
            </td>
            <td>
                <a href="/menorah?candle=1&action=0">OFF</a>
            </td>
        </tr>
    </table>
    <br/><br/><br/>
    <a href="/menorah?init=1">Init</a>
    <br/><br/><br/>
    <a href="/menorah?init=0">Cleanup</a>
</body>
</html>
"""

LIGHT_MAP = {
    1: 3,
    2: 5,
    3: 7,
    4: 11
}

LIGHT_STATE_CLASS_MAP = {
    0: "light-unlit",
    1: "light-lit",
}

def application(environ, start_response):
    status = '200 OK'
    
    try:
        args = urlparse.parse_qs(environ["QUERY_STRING"])
    except Exception as e:
        args = dict()
        raise e
    
    # Init and cleanup
    if "init" in args:
        init_action = int(args["init"][0])
        
        if init_action == 1:
            board_init()
        elif init_action == 0:
            board_cleanup()
    
    # Light on/off
    if ("action" in args) and ("candle" in args):
        action = int(args["action"][0])
        candle = int(args["candle"][0])
        
        if action == 1:
            light_on(candle)
        elif action == 0:
            light_off(candle)
    
    # Get the current light states
    current_light_states = [
        #get_light_state(0),
        0,
        get_light_state(1),
        get_light_state(2),
        get_light_state(3),
        get_light_state(4),
        #get_light_state(5),
        #get_light_state(6),
        #get_light_state(7),
        #get_light_state(8)
        0,
        0,
        0,
        0
    ]
    
    # Output the page
    output = HTML_TEMPLATE.format(
        light_state_8 = LIGHT_STATE_CLASS_MAP[current_light_states[8]],
        light_state_7 = LIGHT_STATE_CLASS_MAP[current_light_states[7]],
        light_state_6 = LIGHT_STATE_CLASS_MAP[current_light_states[6]],
        light_state_5 = LIGHT_STATE_CLASS_MAP[current_light_states[5]],
        light_state_0 = LIGHT_STATE_CLASS_MAP[current_light_states[0]],
        light_state_4 = LIGHT_STATE_CLASS_MAP[current_light_states[4]],
        light_state_3 = LIGHT_STATE_CLASS_MAP[current_light_states[3]],
        light_state_2 = LIGHT_STATE_CLASS_MAP[current_light_states[2]],
        light_state_1 = LIGHT_STATE_CLASS_MAP[current_light_states[1]]
    )
    
    response_headers = [('Content-type', 'text/html'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)
    
    return [output]

def board_init():
    subprocess.check_call(["sudo", "/var/www/html/menorah/board_init.py"])
    
    return "board_init"

def board_cleanup():
    subprocess.check_call(["sudo", "/var/www/html/menorah/board_cleanup.py"])
    
    return "board_cleanup"

def light_on(light_number):
    pin_number = LIGHT_MAP[light_number]
    
    subprocess.check_call(["sudo", "/var/www/html/menorah/board_light_on.py", str(pin_number)])
    
    return "board_light_on"

def light_off(light_number):
    pin_number = LIGHT_MAP[light_number]
    
    subprocess.check_call(["sudo", "/var/www/html/menorah/board_light_off.py", str(pin_number)])
    
    return "board_light_off"

def get_light_state(light_number):
    pin_number = LIGHT_MAP[light_number]
    
    light_state = subprocess.check_output(["sudo", "/var/www/html/menorah/board_light_check.py", str(pin_number)])
    light_state_int = int(light_state.strip())
    
    return light_state_int
