#!/usr/bin/python2

import cwiid
import signal
import sys
import time

import menorah_functions

class WiiRemote():
    # Accelerometer reading required to trigger a light change
    ACC_THRESHOLD = 230
    
    remotes = {1: None, 2: None, 3: None, 4: None}
    
    last_message_time = time.time()
    
    selected_light = 0
    
    @staticmethod
    def listen():
        WiiRemote.remotes[1] = WiiRemote()
        WiiRemote.remotes[1].connect_remote()
    
    def __init__(self):
        self.wiimote = None
        WiiRemote.last_message_time = time.time()
    
    def connect_remote(self):
        while self.wiimote is None:
            try:
                print("Press 1+2 now...")
                self.wiimote = cwiid.Wiimote()
            except RuntimeError:
                time.sleep(1)
        
        self.ack_connection()
        
        self.wiimote.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_ACC
        self.wiimote.enable(cwiid.FLAG_MESG_IFC)
        self.wiimote.mesg_callback = WiiRemote.message_callback
    
    def ack_connection(self):
        """
        Called after a successful pairing
        Vibrates the remote and blinks the LEDs, then turns on LED1
        """
        # Allow an extra second for the connection to be setup
        time.sleep(1)
        
        self.wiimote.rumble = True
        
        leds = [cwiid.LED1_ON, cwiid.LED2_ON, cwiid.LED3_ON, cwiid.LED4_ON]
        
        for led in leds:
            self.wiimote.led = led
            time.sleep(0.5)
        
        self.wiimote.rumble = False
        self.selected_light_to_leds()
        
        print("Battery: %2.1f%%" % (100 * float(self.wiimote.state["battery"]) / cwiid.BATTERY_MAX))
        
        return
    
    def selected_light_to_leds(self):
        if WiiRemote.selected_light == 0:
            self.wiimote.led = 15
        else:
            self.wiimote.led = WiiRemote.selected_light
    
    def close(self):
        self.wiimote.close()
    
    @staticmethod
    def message_callback(message_list, message_time):
        for message in message_list:
            message_type = message[0]
            message_data = message[1]
            
            # Handle accelerometer data
            if message_type == cwiid.MESG_ACC:
                acc_x = message_data[cwiid.X]
                acc_y = message_data[cwiid.Y]
                acc_z = message_data[cwiid.Z]
                
                # If any of the accelerometer reading for any direction exceeds the threshold, trigger a light change
                if (acc_x > WiiRemote.ACC_THRESHOLD) or (acc_y > WiiRemote.ACC_THRESHOLD) or (acc_z > WiiRemote.ACC_THRESHOLD):
                    # Check only once every 2 seconds
                    if message_time > WiiRemote.last_message_time + 2:
                        WiiRemote.last_message_time = message_time
                        menorah_functions.turn_on_next_light(True)
            elif message_type == cwiid.MESG_BTN:
                WiiRemote.last_message_time = message_time
                if message_data == cwiid.BTN_A:
                    menorah_functions.turn_on_next_light(True)
                elif message_data == cwiid.BTN_B:
                    menorah_functions.turn_on_next_light(False)
                elif message_data == cwiid.BTN_LEFT:
                    WiiRemote.selected_light += 1
                    
                    if WiiRemote.selected_light > 8:
                        WiiRemote.selected_light = 0
                    
                    WiiRemote.remotes[1].selected_light_to_leds()
                elif message_data == cwiid.BTN_RIGHT:
                    WiiRemote.selected_light -= 1
                    
                    if WiiRemote.selected_light < 0:
                        WiiRemote.selected_light = 8
                    
                    WiiRemote.remotes[1].selected_light_to_leds()
                elif message_data == cwiid.BTN_UP:
                    menorah_functions.turn_on_light(WiiRemote.selected_light)
                elif message_data == cwiid.BTN_DOWN:
                    menorah_functions.turn_off_light(WiiRemote.selected_light)
                
            elif message_type == cwiid.MESG_ERROR:
                #if message_data == cwiid.ERROR_DISCONNECT:
                WiiRemote.remotes[1].close()
                del WiiRemote.remotes[1]
                WiiRemote.listen()
                return
            
            else:
                print(message)

# Handle SIGQUIT, sent by systemctl stop
def sigquit_handler(signum, stack_frame):
    for i in range(0, len(WiiRemote.remotes)):
        WiiRemote.remotes[i].close()
        del WiiRemote.remotes[i]
    
    sys.exit(0)

signal.signal(signal.SIGQUIT, sigquit_handler)

WiiRemote.listen()

while True:
    time.sleep(0.1)
