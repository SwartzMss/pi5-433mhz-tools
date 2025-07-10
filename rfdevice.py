"""Simple helpers for 433 MHz transmitters and receivers using gpiozero.

These utilities are designed for the Raspberry Pi 5 and provide minimal
functions to send and receive integer codes over cheap RF modules.
"""

from __future__ import annotations
import time
from gpiozero import DigitalInputDevice, DigitalOutputDevice


class RfTransmitter:
    """Transmit integer codes using a 433 MHz transmitter."""

    def __init__(self, pin: int, pulse_length: float = 0.00035) -> None:
        self.device = DigitalOutputDevice(pin)
        self.pulse_length = pulse_length

    def _tx_pulse(self, high_time: float, low_time: float) -> None:
        self.device.on()
        time.sleep(high_time)
        self.device.off()
        time.sleep(low_time)

    def send_code(self, code: int, protocol: int = 1, repeat: int = 10) -> None:
        """Send a binary code using a simple On/Off Keying protocol.

        Parameters
        ----------
        code: int
            The integer code to transmit.
        protocol: int
            Protocol number. Currently only protocol 1 is implemented.
        repeat: int
            Number of times to repeat the code for reliability.
        """
        if protocol != 1:
            raise ValueError("Only protocol 1 is implemented")

        binary = format(code, 'b')
        for _ in range(repeat):
            for bit in binary:
                if bit == '1':
                    self._tx_pulse(self.pulse_length, self.pulse_length * 3)
                else:
                    self._tx_pulse(self.pulse_length, self.pulse_length)
            # sync gap
            time.sleep(self.pulse_length * 31)


class RfReceiver:
    """Receive codes from a 433 MHz receiver."""

    def __init__(self, pin: int, threshold: float = 0.001) -> None:
        self.device = DigitalInputDevice(pin, pull_up=False)
        self.threshold = threshold
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

    def _decode_pulses(self, pulses: list[float]) -> int | None:
        if len(pulses) < 2:
            return None
        binary = ''
        for pulse in pulses:
            binary += '1' if pulse > self.threshold else '0'
        try:
            return int(binary, 2)
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
