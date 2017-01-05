import subprocess
import urlparse

from menorah_functions import *

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
            color: #FFFFFF;
            background-color: #FF4500;
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
    <a href="/menorah?service=1">Restart</a>
    <br/><br/><br/>
    <a href="/menorah?service=0">Stop</a>
</body>
</html>
"""

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
    if "service" in args:
        init_action = int(args["service"][0])
        
        if init_action == 1:
            restart_service()
        elif init_action == 0:
            stop_service()
    
    # Get the current light states
    current_light_states = read_light_state_file()
    
    # Light on/off
    if ("action" in args) and ("candle" in args):
        action = int(args["action"][0])
        candle = int(args["candle"][0])
        
        if action == 1:
            current_light_states[candle] = True
        elif action == 0:
            current_light_states[candle] = False
        
        # Output the new states
        write_light_state_file(current_light_states)
        
        # Send a reload command to the service
        reload_service()

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
