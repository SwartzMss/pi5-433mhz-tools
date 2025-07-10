#!/usr/bin/env python3
"""Listen for 433 MHz codes and print them."""

import argparse

from rfdevice import RfReceiver


def main() -> None:
    parser = argparse.ArgumentParser(description="Receive 433 MHz codes")
    parser.add_argument(
        "--pin", type=int, default=27, help="GPIO pin connected to the receiver"
    )
    parser.add_argument(
        "--protocol", type=int, default=1, help="Reception protocol (default: 1)"
    )
    args = parser.parse_args()

    rx = RfReceiver(args.pin, protocol=args.protocol)
    print("Listening... Press Ctrl+C to exit.")
    try:
        while True:
            code = rx.listen()
            if code is not None:
                print(f"Received {code}")
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
