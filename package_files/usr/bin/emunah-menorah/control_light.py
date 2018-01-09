#!/usr/bin/python

import argparse

import menorah_functions

def parse_args():
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-c", "--control", dest="control", choices=["on", "off", "toggle"], required=True, metavar="CONTROL", help="Turn the light on or off")
    parser.add_argument("-l", "--light", dest="light", type=int, choices=range(0, 9), required=True, metavar="LIGHT", help="The number of the light to turn on or off; allowed values are 0 to 8, where 0 is the shamesh")
    
    args = parser.parse_args()
    
    return args

args = parse_args()

if args.control == "on":
    menorah_functions.turn_on_light(args.light)
elif args.control == "off":
    menorah_functions.turn_off_light(args.light)
elif args.control == "toggle":
    menorah_functions.toggle_light(args.light)
