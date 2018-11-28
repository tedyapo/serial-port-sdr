#!/usr/bin/env python3
"""This module uses common USB-UART bridges as RF trasnmitters."""

import argparse
import time
import serial
import numpy as np
import scipy.io.wavfile
import scipy.signal

# 0xff -_---------
# 0xfd -_-_-------
# 0xf5 -_-_-_-----
# 0xd5 -_-_-_-_---
# 0x55 -_-_-_-_-_-
CODES = [0xff, 0xfd, 0xf5, 0xd5, 0x55]
LEVELS = [1, 2, 3, 4, 5]


# direct pulse-density modulation
def pdm(data):
    """Modulate using character-based pulse density modulation."""
    chars = []
    err = 0
    for val in data:
        err = 2 + 2*val
        idx = max(0, min(4, int(err)))
        code = CODES[idx]
        chars.append(code)
    return chars


# 1-bit delta-sigma DAC
def delta_sigma_1bit(data):
    """Modulate using 1-bit delta-sigma modulation."""
    chars = []
    err = 0
    for val in data:
        err += 1 + val
        if err > 2:
            err -= 2
            chars.append(0x55)
        else:
            chars.append(0xff)
    return chars


# multi-value (2.33 bit) delta-sigma DAC
def delta_sigma_multivalue(data):
    """Modulate using multilevel delta-sigma modulation."""
    chars = []
    err = 0
    for val in data:
        err += 2 + 2*val
        idx = max(0, min(4, int(err)))
        code = CODES[idx]
        chars.append(code)
        err -= LEVELS[idx]
    return chars


def main():
    """Transmit AM-modulated RF using serial port."""
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file',
                        help='audio file (wav format) to transmit')
    parser.add_argument('port', help='serial port device name')
    parser.add_argument('-s', '--start_offset',
                        help='audio start point (seconds)',
                        type=float, default=0)
    parser.add_argument('-e', '--end_offset', help='audio end point (seconds)',
                        type=float)
    parser.add_argument('-r', '--rate', help='audio resample rate',
                        dest='audio_rate', type=int, default=11025)
    parser.add_argument('-b', '--baud', help='baud rate',
                        dest='baud_rate', type=float, required=True)
    parser.add_argument('-m', '--method', help='modulation method',
                        dest='modulation',
                        choices=['pdm', 'ds1bit', 'dsmulti'],
                        default='dsmulti')
    parser.add_argument('-l', '--loop', help='transmit continuously',
                        dest='loop', action='store_true')
    parser.add_argument('-d', '--delay', help='delay between loops',
                        dest='delay', type=float, default=1.)

    args = parser.parse_args()

    ser = serial.Serial(args.port, args.baud_rate)

    input_rate, data = scipy.io.wavfile.read(args.input_file)

    # if input file is stereo, mix down to mono
    if data.shape[1] == 2:
        data = np.mean(data, 1)

    # extract selected part of audio
    if args.end_offset:
        data = data[int(args.start_offset*input_rate):
                    int(args.end_offset*input_rate)]
    else:
        data = data[int(args.start_offset*input_rate):]

    # resample to target audio rate
    #   this low-pass filters in the case of high-sample-rate inputs
    if input_rate != args.audio_rate:
        data = scipy.signal.resample_poly(data, args.audio_rate, input_rate)

    # resample again to the character rate (baudrate/10)
    data = scipy.signal.resample_poly(data, int(args.baud_rate),
                                      10*args.audio_rate)

    # remove mean and scale to +/-1 amplitude
    data = data - np.mean(data)
    data = data/np.max(np.abs(data))

    # modulate
    if args.modulation == 'pdm':
        chars = pdm(data)
    elif args.modulation == 'ds1bit':
        chars = delta_sigma_1bit(data)
    elif args.modulation == 'dsmulti':
        chars = delta_sigma_multivalue(data)

    stream = bytes(chars)

    if args.loop:
        while True:
            ser.write(stream)
            time.sleep(args.delay)
    else:
        ser.write(stream)


if __name__ == '__main__':
    main()
