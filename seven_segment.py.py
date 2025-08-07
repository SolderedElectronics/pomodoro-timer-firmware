
# MicroPython class for 4-digit 7-segment display (common cathode)
# Compatible with RP2040 boards
# Author: Soldered (https://soldered.com)

import time
import machine

class SevenSegmentDisplay:
    SEG_ON = 1
    SEG_OFF = 0
    DIG_ON = 0
    DIG_OFF = 1
    REFRESH_MS = 1

    def __init__(self, segment_pins, digit_pins, dp_pin=None):
        self.segments = [machine.Pin(p, machine.Pin.OUT) for p in segment_pins]
        self.digits = [machine.Pin(p, machine.Pin.OUT) for p in digit_pins]
        self.dp = machine.Pin(dp_pin, machine.Pin.OUT) if dp_pin is not None else None

        self.patterns = {
            '0': [1,1,1,1,1,1,0], '1': [0,1,1,0,0,0,0],
            '2': [1,1,0,1,1,0,1], '3': [1,1,1,1,0,0,1],
            '4': [0,1,1,0,0,1,1], '5': [1,0,1,1,0,1,1],
            '6': [1,0,1,1,1,1,1], '7': [1,1,1,0,0,0,0],
            '8': [1,1,1,1,1,1,1], '9': [1,1,1,1,0,1,1],
            '-': [0,0,0,0,0,0,1], ' ': [0,0,0,0,0,0,0]
        }

        self.clear()

    def clear(self):
        for d in self.digits:
            d.value(self.DIG_OFF)
        for s in self.segments:
            s.value(self.SEG_OFF)
        if self.dp:
            self.dp.value(self.SEG_OFF)

    def show_char(self, digit_index, ch, dot=False):
        pattern = self.patterns.get(ch, [0]*7)
        for seg_pin, bit in zip(self.segments, pattern):
            seg_pin.value(self.SEG_ON if bit else self.SEG_OFF)
        if self.dp:
            self.dp.value(self.SEG_ON if dot else self.SEG_OFF)

        self.digits[digit_index].value(self.DIG_ON)
        time.sleep_ms(self.REFRESH_MS)
        self.digits[digit_index].value(self.DIG_OFF)

    def show_frame(self, frame, duration_ms=1000):
        end = time.ticks_add(time.ticks_ms(), duration_ms)
        while time.ticks_diff(end, time.ticks_ms()) > 0:
            for i, ch in enumerate(frame):
                self.show_char(i, ch)

