# Flipdot Simulator and Driver

This program implements a [Pillow](https://github.com/python-pillow/Pillow) (Python
Imaging Library friendly fork) driver and simulator for the [Flip-Dot XY5
Display](https://flipdots.com/en/products-services/flip-dot-boards-xy5/) from
[AlphaZeta](https://flipdots.com/en/home/).


## The Flip-Dot Display

The XY5 Display can be thought of as a bitmaped screen. It consists of mechanical
flipping "dots," laid out in an XY grid. The display is made up of a number of
individual panels, where each panel is 7x28 pixels. Each panel has a controller, and
the controllers may be daisy-chained. Controllers connect to driver computers via
RS-485. On a single daisy-chain, each panel gets a unique numeric address (0, 1, 2, etc..).

The protocol to control a panel is not well-documented. Essentially each column of 7
pixels (in a 7x28 board) is a controlled by a single byte, using the lower seven
bits. The packet header includes panel address information, as well as other
meta-data. The protocol is outlined more in the [reference
code](https://github.com/dcreemer/flipdot/blob/master/docs/XY5_arduino.txt) from
Alfa-Zeta.

## Driver

For developing interesting visualizations, it's much nice to treat a collection of
panels as an 1-bit-per-pixel arbitrary XY image. This software implements that
abstraction using the Python Imaging Library. Image data is rendered into an image,
and then periodically that image is converted to Flip-Dot display protocol and sent
to the panels. To make development easier, this software also implements a
curses-based simulator of the display that communicated via UDP. Develop on a local
computer, then try it out on a real display.

## Usage

```sh
# Create virtualenv and install the required libraries with pipenv:
pipenv install
```

```sh
# Run the simulator in one window
pipenv run python flipdot/sim.py
```

In another, run the demo application (defaults to same setup as simulator):

```sh
pipenv run python cli.py
```

See --help flags for more usage

```sh
pipenv run flipdot/sim.py --help
pipenv run cli.py --help
```

## Samples

```sh
 ----------------------------------------------------------
| ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○  |
| ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○  |
| ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○  |
| ● ● ○ ○ ● ● ○ ● ● ● ○ ○ ○ ● ● ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○  |
| ● ● ○ ○ ● ● ● ● ○ ● ● ○ ○ ● ● ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○  |
| ○ ● ● ● ● ○ ● ● ○ ● ● ○ ○ ● ● ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○  |
| ○ ○ ● ● ○ ○ ● ● ○ ● ● ○ ○ ● ● ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○  |
| ○ ○ ● ● ○ ○ ● ● ○ ● ● ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○  |
| ○ ● ● ● ● ○ ○ ● ● ● ○ ○ ○ ● ● ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○  |
| ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○  |
| ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○  |
| ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○  |
| ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○  |
| ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○  |
 ----------------------------------------------------------
```

Here is a sample video:

[![sample flip-dot video](https://img.youtube.com/vi/toKsp2REu5E/0.jpg)](https://www.youtube.com/watch?v=toKsp2REu5E) 

(click the image to play it). It shows this software running a live Flip-Dot display,
cycling through headlines derived from [Flipboard](https://about.flipboard.com/).

## Develop

See the `demo.py` file for examples, but in general, anything that can be written to
a Python Imaging Library 1-bit image can be sent to the display. The code should be
fine on Python 2.7.X and Python 3.6.X.

### License

BSD 3-Clause. Note that the included font "VeraBd.ttf" is from
[here](https://www.gnome.org/fonts/) and subject to its own license.
