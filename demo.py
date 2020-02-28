#! /usr/bin/env python

import sys
import time

from demo import animations
from flipdot import client, display

# 9 x 3, 28 x 14 panels in PORTRAIT!
PANEL_X = 28
PANEL_Y = 7
MATRIX_SIZE_X = 1
MATRIX_SIZE_Y = 8
MATRIX_X = MATRIX_SIZE_X * PANEL_X
MATRIX_Y = MATRIX_SIZE_Y * PANEL_Y

def create_display(panel_size, display_size):
    ret = {}
    addr = 1
    cord = [0, 0]

    for x in range(0, display_size[0], panel_size[0]):
        for y in range(0, display_size[1], panel_size[1]):
            cord = [x, y]
            ret[addr] = (cord, panel_size)
            addr += 1

    print(ret)
    return ret


d1 = display.Display(MATRIX_X, MATRIX_Y, create_display((PANEL_X, PANEL_Y), (MATRIX_X, MATRIX_Y)))
d2 = display.Display(MATRIX_X, MATRIX_Y, create_display((PANEL_X, PANEL_Y), (MATRIX_X, MATRIX_Y)))

multi = {
        1: ((0, 0), d1),
        2: ((0, 56), d2)
        }

d = display.MultiDisplay(28, 56*2, multi)

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
    if len(sys.argv) > 1 and sys.argv[1] == "udp":
        d1.connect(client.UDPClient("localhost", 9999))
        d2.connect(client.UDPClient("localhost", 9998))
    elif len(sys.argv) > 1 and sys.argv[1] == "tcp":
        d1.connect(client.TCPClient("localhost", 9999))
        d2.connect(client.TCPClient("localhost", 9998))
    else:
        d1.connect(client.SerialClient('/dev/ttyUSB1'))
        d2.connect(client.SerialClient('/dev/ttyUSB2'))
    try:
        # intro(d)
        while True:
            mainloop(d)
            time.sleep(5)
    finally:
        d1.disconnect()
        d2.disconnect()


if __name__ == "__main__":
    main()
