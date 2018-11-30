#!/usr/bin/env python3
"""Output a square wave on serial port TX line"""

import argparse
import serial


def main():
    """Generate square wave using serial port."""
    parser = argparse.ArgumentParser(description='Generate square wave from' +
                                     ' serial port')
    parser.add_argument('port', help='serial port device name')
    parser.add_argument('frequency', help='output frequency (Hz)',
                        type=float)
    args = parser.parse_args()

    baud_rate = int(2 * args.frequency)

    data = bytes([0x55]*baud_rate)
    ser = serial.Serial(args.port, baud_rate)
    while True:
        ser.write(data)


if __name__ == '__main__':
    main()
