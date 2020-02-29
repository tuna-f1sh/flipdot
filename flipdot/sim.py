#! /usr/bin/env python
#
# python flipdot display simulator


from __future__ import print_function
import sys

import curses
import threading
import time

if sys.version_info.major == 2:
    import SocketServer as socketserver
else:
    import socketserver

from PIL import Image, ImageOps

import display


RefreshRate = 0.2
sim = None
stdscr = None

class Handler(socketserver.BaseRequestHandler):

    def handle(self):
        pass

    def validate(self, raw):
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

    def update_display(self, data):
        address = data[2]
        # if data[1] in (0x82, 0x83, 0x85):
        #     sim.refresh(address)
        body = data[3:-1]
        # print("SIM", address, len(body), list(body))
        sim.update(address, body)

class TCPHandler(Handler):

    def handle(self):
        try:
            data = self.request.recv(1024).strip()
            data = self.validate(data)
            if data:
                self.update_display(data)
        finally:
            self.request.close()
            pass

class UDPHandler(Handler):

    def handle(self):
        data = self.request[0]
        data = self.validate(data)
        if data:
            self.update_display(data)

class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def start_server():
    if len(sys.argv) > 1:
        HOST, PORT = "localhost", int(sys.argv[1])
    else:
        HOST, PORT = "localhost", 9999
    server = ThreadedUDPServer((HOST, PORT), UDPHandler)
    # server = ThreadedTCPServer((HOST, PORT), TCPHandler)
    ip, port = server.server_address
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()


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
            # print '\033c', self.frames
            with self.l:
                self.draw()
            time.sleep(RefreshRate)

    def draw(self):
        px = self.d.im.load()
        w, h = self.d.im.size
        r = w*2+3
        onoff = {True: " ●", False: " ○"}
        stdscr.addstr(0, 1, "-"*r)
        stdscr.addstr(h+1, 1, "-"*r)
        for y in range(h):
            stdscr.addstr(y+1, 0, "|")
            stdscr.addstr(y+1, r+1, "|")
            for x in range(w):
                v = self.d.px_to_bit(px[x, y])
                stdscr.addstr(y+1, 2+x*2, onoff[v])
        stdscr.refresh()

    def refresh(self, address=None):
        with self.l:
            self.d.reset(address)

    def update(self, address, data):
        # update the internal image from the given list of bytes
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
            if (self.portrait):
                n = n.rotate(angle=-90, expand=1)
                x = ImageOps.mirror(n)
                # n = n.tranpose(Image.FLIP_LEFT_RIGHT)
                # self.d.im.paste(n, box=(ys, xs))
                # sz = (ys + h, xs + w)
                # ix, iy = self.d.size
                self.d.im.paste(x, box=(ys, xs))
            else:
                self.d.im.paste(n, box=(xs, ys))



def init_curses():
    global stdscr
    stdscr = curses.initscr()
    curses.noecho()


def stop_curses():
    curses.echo()
    curses.endwin()

# Need to swap cords and size for flipped sim (no work!)
PANELS = {1: ([0, 0], (28, 7)), 2: ([0, 7], (28, 7)), 3: ([0, 14], (28, 7)), 4: ([0, 21], (28, 7)), 5: ([0, 28], (28, 7)), 6: ([0, 35], (28, 7)), 7: ([0, 42], (28, 7)), 8: ([0, 49], (28, 7))}
# PANELS = {1: ([0, 0], (28, 7)), 2: ([7, 0], (28, 7)), 3: ([14, 0], (28, 7)), 4: ([21, 0], (28, 7)), 5: ([28, 0], (28, 7)), 6: ([35, 0], (28, 7)), 7: ([42, 0], (28, 7)), 8: ([49, 0], (28, 7))}


if __name__ == "__main__":
    sim = DisplaySim(28, 56, PANELS)
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
