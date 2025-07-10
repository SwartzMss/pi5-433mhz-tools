#!/usr/bin/env python3
"""Transmit integer codes using a 433 MHz transmitter."""

import argparse
from rfdevice import RfTransmitter


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a 433 MHz code")
    parser.add_argument('--pin', type=int, default=17,
                        help='GPIO pin connected to the transmitter')
    parser.add_argument('code', type=int, help='Integer code to transmit')
    args = parser.parse_args()

    tx = RfTransmitter(args.pin)
    tx.send_code(args.code)
    print(f"Sent {args.code}")


if __name__ == '__main__':
    main()
