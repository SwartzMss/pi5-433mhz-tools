#!/usr/bin/env python3
"""Transmit integer codes using a 433 MHz transmitter."""

import argparse

from rfdevice import RfTransmitter


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a 433 MHz code")
    parser.add_argument(
        "--pin", type=int, default=17, help="GPIO pin connected to the transmitter"
    )
    parser.add_argument(
        "--protocol", type=int, default=1, help="Transmission protocol (default: 1)"
    )
    parser.add_argument("code", type=int, help="Integer code to transmit")
    parser.add_argument(
        "--repeat", type=int, default=1, help="Number of times to repeat the code"
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Delay in seconds between repeated transmissions",
    )
    args = parser.parse_args()

    tx = RfTransmitter(args.pin, protocol=args.protocol)
    tx.send_code(args.code, repeat=args.repeat, interval=args.interval)
    print(f"Sent {args.code}")


if __name__ == "__main__":
    main()
