#!/usr/bin/python

import cwiid
import time

class WiiRemote():
    # Accelerometer reading required to trigger a light change
    ACC_THRESHOLD = 230
    
    def __init__(self):
        self.wiimote = None
        self.last_message_time = time.time()
    
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
        self.wiimote.rumble = True
        
        leds = [cwiid.LED1_ON, cwiid.LED2_ON, cwiid.LED3_ON, cwiid.LED4_ON]
        
        for led in leds:
            self.wiimote.led = led
            time.sleep(0.5)
        
        self.wiimote.rumble = False
        self.wiimote.led = cwiid.LED1_ON
        
        return
    
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
                    # Check only once every 3 seconds
                    if message_time > self.last_message_time + 3:
                        self.last_message_time = message_time
                        print("message_callback")
                        print 'Acc Report: x=%d, y=%d, z=%d' % (message_data[cwiid.X], message_data[cwiid.Y], message_data[cwiid.Z])

wiiremote1 = WiiRemote()
wiiremote1.connect_remote()

while True:
    time.sleep(0.1)
