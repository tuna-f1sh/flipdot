#! /usr/bin/env python

import random
import os.path
import time

from PIL import Image, ImageDraw, ImageFont


def rsrc(n):
    return os.path.join(os.path.dirname(__file__), n)


a1 = Image.open(rsrc("images/a1.png"))
a2 = Image.open(rsrc("images/a2.png"))
frames1 = {0: a1, 1: a1, 2: a2, 3: a2}

b1 = Image.open(rsrc("images/b1.png"))
b2 = Image.open(rsrc("images/b2.png"))
frames2 = {0: b1, 1: b1, 2: b2, 3: b2}

p1 = Image.open(rsrc("images/p1.png"))
p2 = Image.open(rsrc("images/p2.png"))
frames3 = {0: p1, 1: p1, 2: p2, 3: p2}

BigFont = ImageFont.truetype(rsrc("fonts/VeraBd.ttf"), 15)
SmallFont = None


def scroll_text(d, text, font=BigFont, xy=(1,1), rotate=False):
    draw = ImageDraw.Draw(d.im)
    tw, th = draw.textsize(text, font=font)
    for x in range(xy[0], 0-tw, -1):
        if rotate: d.im = d.im.rotate(angle=90, expand=1)
        d.reset()
        draw.text((x, xy[1]), text, font=font)
        if rotate: d.im = d.im.rotate(angle=-90, expand=1)
        d.send()
        time.sleep(0.06)
    del draw


def display_text(d, text, xy=(1,1), font=SmallFont, rotate=False):
    # rotate so that text is entered with w/h flipped
    if rotate: d.im = d.im.rotate(angle=90, expand=1)
    draw = ImageDraw.Draw(d.im)
    tw, th = draw.textsize(text, font=font)
    shift = -1 if font == BigFont else -3
    d.reset()
    draw.text(xy, text, font=font)
    # now rotate the image back to display format
    if rotate: d.im = d.im.rotate(angle=-90, expand=1)
    d.send()
    del draw


def blink_text(d, text, n=3):
    for i in range(n):
        display_text(d, text)
        time.sleep(0.5)
        d.reset()
        d.send()
        time.sleep(0.5)


def animate(disp, i, w, d=1):
    l, h = -w, 29
    if d < 0:
        l, h = h, l
    for x in range(l, h, d):
        im = i[abs(x % len(i))]
        disp.reset()
        disp.im.paste(im, (x, 0))
        disp.send()
        time.sleep(0.1)


#
# animations:
#

def alien_1(d):
    animate(d, frames1, d.im.size[0], 1)


def alien_2(d):
    animate(d, frames2, d.im.size[0], -1)


def gobble(d):
    animate(d, frames3, d.im.size[0], 1)


def dot(d):
    draw = ImageDraw.Draw(d.im)
    w, h = d.im.size
    mw = w/2
    mh = h/2
    for i in range(0, 7):
        d.reset()
        draw.ellipse([(mw-i, mh-i), (mw+i, mh+i)], fill=(255, 255, 255))
        d.send()
        time.sleep(0.6 / (i+1))
    del draw


def wipe_right(d):
    w, h = d.im.size
    d.reset(white=True)
    d.send()
    time.sleep(0.5)
    for x in range(1, w+1):
        draw = ImageDraw.Draw(d.im)
        xy = (0, 0)
        sz = (x, h)
        draw.rectangle([xy, sz], fill=(0, 0, 0))
        del draw
        d.send()
        time.sleep(0.07)


def wipe_down(d):
    w, h = d.im.size
    d.reset()
    d.send()
    time.sleep(0.5)
    for y in range(1, h+1):
        draw = ImageDraw.Draw(d.im)
        xy = (0, 0)
        sz = (w, y)
        draw.rectangle([xy, sz], fill=(255, 255, 255))
        del draw
        d.send()
        time.sleep(0.1)


def curtain(d):
    w, h = d.im.size
    for x in range(1, w+1):
        draw = ImageDraw.Draw(d.im)
        xy = (w-x, 0)
        sz = (x, h)
        draw.rectangle([(0, 0), (w, h)], fill=(255, 255, 255))
        draw.rectangle([xy, sz], fill=(0, 0, 0))
        del draw
        d.send()
        time.sleep(0.1)


transitions = [
    dot,
    alien_1,
    alien_2,
    curtain,
    wipe_right,
    wipe_down,
    gobble,
    ]
random.shuffle(transitions)
t_idx = 0


def rand(d):
    global t_idx
    f = transitions[t_idx]
    t_idx = (t_idx + 1) % len(transitions)
    f(d)
