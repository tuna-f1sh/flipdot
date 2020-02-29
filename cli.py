#! /usr/bin/env python

import sys
import time

from demo import animations
from flipdot import client, display
import argparse

parser = argparse.ArgumentParser(description='Run an Alfa-Zeta flot-dot client')
parser.add_argument('-P','--protocol', type=str, choices=['tcp', 'udp', 'usb'],
                    default='udp',
                    help='communication protocol to use')
parser.add_argument('-p','--port', type=int, default=5000,
                    help='port of Ethernet->RS485 device')
parser.add_argument('-i','--ip', type=str, default='localhost',
                    help='ip address of Ethernet->RS485 device')
parser.add_argument('-u','--usb', type=str, default='/dev/ttyUSB0',
                    help='usb port of USB->RS485 device')
parser.add_argument('-x','--width', type=int, default=28,
                    help='display width, should be multiple of panel width 28')
parser.add_argument('-y','--height', type=int, default=14,
                    help='display height, should be multiple of panel height 7')
parser.add_argument('text', type=str, nargs='?', default='',
                    help='text to display')
parser.add_argument('--demo', action='store_true',
                    help='run demo routine')
parser.add_argument('--portrait', action='store_true',
                    help='panels are in portrait orientation')
parser.add_argument('--blink', action='store_true',
                    help='blink text')
parser.add_argument('--stdout', action='store_true',
                    help='print display config')
# TODO - add log output
parser.add_argument('-v','--verbose', action='store_true',
                    help='enabling verbose debugging output')
args = parser.parse_args()

PANEL_X = 28
PANEL_Y = 7

d = display.Display(args.width, args.height, display.create_display((PANEL_X, PANEL_Y), (args.width, args.height)))
if args.stdout: print(d.panels)

def transition(d):
    animations.rand(d)

def mainloop(d):
    animations.display_text(d, "YO!")
    time.sleep(2)
    transition(d)
    animations.blink_text(d, "HI!")
    time.sleep(1)
    transition(d)
    animations.scroll_text(d, "This is scrolled text.", font=animations.SmallFont)
    time.sleep(0.5)
    transition(d)
    d.reset()
    d.send()

def main():
    if args.protocol == 'udp':
        d.connect(client.UDPClient(args.ip, args.port))
    elif args.protocol == 'tcp':
        d.connect(client.TCPClient(args.ip, args.port))
    elif args.protocol == 'rs485':
        d.connect(client.SerialClient(args.usb))
    try:
        d.reset(white=True)
        while True:
            if args.demo or args.text == '':
                mainloop(d)
            else:
                if args.blink:
                    animations.blink_text(d, args.text)
                else:
                    animations.display_text(d, args.text)
            time.sleep(1)
    finally:
        d.disconnect()

if __name__ == "__main__":
    main()
