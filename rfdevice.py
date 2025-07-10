"""Simple helpers for 433 MHz transmitters and receivers using gpiozero.

These utilities are designed for the Raspberry Pi 5 and provide minimal
functions to send and receive integer codes over cheap RF modules.
"""

from __future__ import annotations

import time
from typing import Dict

from gpiozero import DigitalInputDevice, DigitalOutputDevice

PROTOCOLS: Dict[int, Dict[str, float]] = {
    1: {
        "pulselength": 350,
        "sync_high": 1,
        "sync_low": 31,
        "zero_high": 1,
        "zero_low": 3,
        "one_high": 3,
        "one_low": 1,
        "tolerance": 0.35,
    }
}


class RfTransmitter:
    """Transmit integer codes using a 433 MHz transmitter."""

    def __init__(self, pin: int, protocol: int = 1) -> None:
        if protocol not in PROTOCOLS:
            raise ValueError(f"Unsupported protocol {protocol}")

        self.device = DigitalOutputDevice(pin)
        self.protocol = protocol
        # ``pulselength`` is stored in seconds internally
        pl_us = PROTOCOLS[protocol]["pulselength"]
        self.pulse_length = pl_us / 1_000_000

    def _tx_pulse(self, high_time: float, low_time: float) -> None:
        self.device.on()
        time.sleep(high_time)
        self.device.off()
        time.sleep(low_time)

    def send_code(
        self, code: int, protocol: int | None = None, repeat: int = 10
    ) -> None:
        """Send a binary code using the selected protocol.

        Parameters
        ----------
        code: int
            The integer code to transmit.
        protocol: int | None
            Protocol number. If ``None`` the transmitter's default is used.
        repeat: int
            Number of times to repeat the code for reliability.
        """
        proto_num = protocol or self.protocol
        if proto_num not in PROTOCOLS:
            raise ValueError(f"Unsupported protocol {proto_num}")

        proto = PROTOCOLS[proto_num]
        pl = (
            self.pulse_length
            if proto_num == self.protocol
            else proto["pulselength"] / 1_000_000
        )

        binary = format(code, "b")
        for _ in range(repeat):
            for bit in binary:
                if bit == "1":
                    self._tx_pulse(proto["one_high"] * pl, proto["one_low"] * pl)
                else:
                    self._tx_pulse(proto["zero_high"] * pl, proto["zero_low"] * pl)
            # sync gap
            self._tx_pulse(proto["sync_high"] * pl, proto["sync_low"] * pl)


class RfReceiver:
    """Receive codes from a 433 MHz receiver."""

    def __init__(self, pin: int, protocol: int = 1) -> None:
        if protocol not in PROTOCOLS:
            raise ValueError(f"Unsupported protocol {protocol}")

        self.device = DigitalInputDevice(pin, pull_up=False)
        self.protocol = protocol
        proto = PROTOCOLS[protocol]
        self.pulse_length = proto["pulselength"] / 1_000_000
        self.tolerance = proto["tolerance"]
        self.last_code: int | None = None
        self.last_timestamp: float | None = None

    def _record_pulses(self, duration: float = 0.02) -> list[float]:
        pulses = []
        start = time.monotonic()
        last_time = start
        last_state = self.device.value
        while time.monotonic() - start < duration:
            state = self.device.value
            if state != last_state:
                now = time.monotonic()
                pulses.append(now - last_time)
                last_time = now
                last_state = state
        return pulses

    def _within(self, actual: float, expected_factor: float) -> bool:
        expected = expected_factor * self.pulse_length
        return (
            expected * (1 - self.tolerance) <= actual <= expected * (1 + self.tolerance)
        )

    def _decode_pulses(self, pulses: list[float]) -> int | None:
        if len(pulses) < 2:
            return None

        proto = PROTOCOLS[self.protocol]
        bits = ""
        i = 0
        while i + 1 < len(pulses):
            high = pulses[i]
            low = pulses[i + 1]
            i += 2

            if self._within(high, proto["sync_high"]) and self._within(
                low, proto["sync_low"]
            ):
                bits = ""
                continue

            if self._within(high, proto["zero_high"]) and self._within(
                low, proto["zero_low"]
            ):
                bits += "0"
                continue

            if self._within(high, proto["one_high"]) and self._within(
                low, proto["one_low"]
            ):
                bits += "1"
                continue

            return None

        if not bits:
            return None
        try:
            return int(bits, 2)
        except ValueError:
            return None

    def listen(self, listen_time: float = 0.02) -> int | None:
        """Listen for a single code.

        Parameters
        ----------
        listen_time: float
            How long to capture pulses in seconds.
        """
        pulses = self._record_pulses(listen_time)
        code = self._decode_pulses(pulses)
        if code is not None:
            self.last_code = code
            self.last_timestamp = time.time()
        return code
