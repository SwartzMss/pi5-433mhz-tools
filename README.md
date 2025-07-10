# pi5-433mhz-tools

Minimal 433 MHz communication helpers for the Raspberry Pi 5 using
[gpiozero](https://gpiozero.readthedocs.io/).

## Components

- `rfdevice.py` – Helper classes for sending and receiving codes.
- `sender.py` – Send a single integer code.
- `receive.py` – Listen and print received codes.

## Usage

Send a code on GPIO 17:

```bash
python3 sender.py --pin 17 --protocol 1 1234
```

Listen for codes on GPIO 27:

```bash
python3 receive.py --pin 27 --protocol 1
```

![Uploading ff86c80f28d74ef6044f84b0d14ae1f.jpg…]()


## License

This project is released under the MIT license.
