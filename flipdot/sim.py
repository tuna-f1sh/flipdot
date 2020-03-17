#! /usr/bin/env python
#
# python flipdot display simulator


from __future__ import print_function
import sys

import curses
import threading
import time
import serial

if sys.version_info.major == 2:
    import SocketServer as socketserver
else:
    import socketserver

from PIL import Image, ImageOps

import display

import argparse

parser = argparse.ArgumentParser(description='Run a tui Alfa-Zeta flot-dot simulation')
parser.add_argument('-P','--protocol', type=str, choices=['tcp', 'udp', 'usb'],
                    default='udp',
                    help='communication protocol to use')
parser.add_argument('-r','--refresh', type=float, default=0.2,
                    help='panel refresh rate in seconds')
parser.add_argument('-p','--port', type=int, default=5000,
                    help='network port to use on localhost')
parser.add_argument('-u','--usb', type=str, default='/dev/ttyUSB0',
                    help='usb port of USB->RS485 device')
parser.add_argument('-x','--width', type=int, default=28,
                    help='display width, should be multiple of panel width 28')
parser.add_argument('-y','--height', type=int, default=14,
                    help='display height, should be multiple of panel height 7')
parser.add_argument('--portrait', action='store_true',
                    help='panels are in portrait orientation so rotate tui for display')
parser.add_argument('-v','--verbose', action='store_true',
                    help='enabling verbose debugging output')
args = parser.parse_args()

RefreshRate = args.refresh
NetworkLatency = 0.01
sim = None
stdscr = None
debugPos = (args.width+3, 1) if args.portrait else (args.height+3, 1)

class Handler(socketserver.BaseRequestHandler):

    def handle(self):
        pass

    @staticmethod
    def validate(raw):
        if sys.version_info.major == 2:
            data = [ord(x) for x in raw]
        else:
            data = raw
        if data[0] != 0x80:
            print("no start")
            return []
        if data[1] not in (0x81, 0x82, 0x83, 0x84, 0x85, 0x86):
            print("not right command")
            return []
        ln = 0
        if data[1] in (0x81, 0x82):
            ln = 112
        elif data[1] in (0x83, 0x84):
            ln = 28
        elif data[1] in (0x85, 0x86):
            ln = 56
        if len(data) != (ln + 4):
            print("bad length", len(data))
            return []
        if data[-1] != 0x8F:
            print("no end")
            return []
        return data

    @staticmethod
    def update_display(data):
        address = data[2]
        body = data[3:-1]
        if args.verbose:
            debug = "ADR: {} DATA: {}".format(address, ' '.join('{:02X}'.format(x) for x in data))
            stdscr.addstr(debugPos[0]+address, debugPos[1], debug, curses.color_pair(3))
        sim.update(address, body)

class TCPHandler(Handler):

    def handle(self):
        """
        handle will close socket on return so stay here waiting for recv (will
        return 0 on break) this behavior is like the Ethernet -> RS485 boxes.
        Socket is blocking but this is a thread so it's ok
        """
        while 1:
            data = bytearray()
            chunk = None
            self.request.settimeout(5)
            # unload until we get the end of frame char (or client disconnect)
            while chunk != b"\x8F":
                chunk = self.request.recv(1)
                # client closed so return and close server connection
                if chunk == b"":
                    return
                data.extend(chunk)
            if len(data) > 0:
                data = self.validate(data)
                self.update_display(data)
            time.sleep(NetworkLatency)

class UDPHandler(Handler):

    def handle(self):
        data = self.request[0]
        data = self.validate(data)
        if data:
            self.update_display(data)

class SerialHandler():
    def __init__(self, port):
        self.chan = serial.Serial()
        self.chan.baudrate = 57600
        self.chan.port = port
        self.chan.timeout = 10.0
        self.thread = threading.Thread(target=self.read_from_port)
        self.thread.daemon = True

    def open(self):
        self.chan.open()
        self.thread.start()

    def close(self):
        self.chan.close()

    def read_from_port(self):
        while True:
            if self.chan.in_waiting > 0:
                data = self.chan.read_until(b"\x8F")
                if data: self.handle(data)

    def handle(self, data):
        data = Handler.validate(data)
        if data:
            Handler.update_display(data)

class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def start_server():
    if args.protocol != 'usb':
        if args.protocol == 'tcp':
            server = ThreadedTCPServer(("localhost", args.port), TCPHandler)
        elif args.protocol == 'udp':
            server = ThreadedUDPServer(("localhost", args.port), UDPHandler)
        else:
            raise ValueError('Invalid protocol')
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
    else:
        server = SerialHandler(args.usb)
        server.open()



class DisplaySim(threading.Thread):

    def __init__(self, w, h, panels=None, portrait=False):
        super(DisplaySim, self).__init__()
        self.d = display.Display(w, h, panels)
        self.l = threading.RLock()
        self.frames = 0
        self._stop = threading.Event()
        self.portrait = portrait

    def stop(self):
        self._stop.set()
        self.join()

    def run(self):
        while not self._stop.is_set():
            self.frames += 1
            with self.l:
                self.draw()
            time.sleep(RefreshRate)

    def draw(self):
        if self.portrait:
            px = self.d.im.rotate(angle=-90, expand=1).load()
            h, w = self.d.im.size
        else:
            px = self.d.im.load()
            w, h = self.d.im.size
        # length of - to print for horizontal frame
        r = w*2+2
        onoff = {True: "●", False: "○"}
        stdscr.addstr(0, 1, "-"*r, curses.color_pair(2))
        stdscr.addstr(h+1, 1, "-"*r, curses.color_pair(2))
        for y in range(h):
            stdscr.addstr(y+1, 0, "|", curses.color_pair(2))
            stdscr.addstr(y+1, r+1, "|", curses.color_pair(2))
            for x in range(w):
                v = self.d.px_to_bit(px[x, y])
                stdscr.addstr(y+1, 2+x*2, onoff[v], curses.color_pair(1))
        stdscr.refresh()

    def refresh(self, address=None):
        with self.l:
            self.d.reset(address)

    def update(self, address, data):
        # update the internal image from the given list of bytes
        if address in self.d.panels.keys():
            (xs, ys), (w, h) = self.d.panels[address]
            n = Image.new("RGB", (w, h))
            if h != 7:
                print("H is not 7!!!")
            for x in range(w):
                # get the next byte
                b = data[x]
                for y in range(h):  # note that h should always be 7
                    px = b & 0x01
                    b = b >> 1
                    if px:
                        n.putpixel((x, y), (255, 255, 255))
            with self.l:
                self.d.im.paste(n, box=(xs, ys))



def init_curses():
    global stdscr
    stdscr = curses.initscr()
    curses.start_color()
    # dots
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    # frame
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.curs_set(0)
    curses.noecho()

    if args.verbose: 
        stdscr.addstr(*debugPos, 
            "W: {} H: {} Portrait: {} Panels: {} Panel size: {} Port: {}".format(args.width, args.height, args.portrait,
            len(sim.d.panels), sim.d.panels[1][1], args.port),
            curses.color_pair(2))
        stdscr.addstr(debugPos[0]+1, debugPos[1], "Waiting for first data packet...", curses.color_pair(3))
    else:
        # make sure term is right size
        if args.portrait:
            curses.resize_term(args.width*2+4, args.height*2+4)
        else:
            curses.resize_term(args.height*2+4, args.width*2+4)



def stop_curses():
    curses.echo()
    curses.endwin()


if __name__ == "__main__":
    sim = DisplaySim(args.width, args.height, display.create_display((28, 7), (args.width, args.height)), portrait=args.portrait)
    try:
        init_curses()
        sim.start()
        start_server()
        try:
            while True:
                time.sleep(0.01)
        except KeyboardInterrupt:
            pass
        sim.stop()
    finally:
        stop_curses()
