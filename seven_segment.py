# FILE: seven_segment.py
# AUTHOR: Štefan Granatir, Josip Šimun Kuči @ Soldered (original)
# BRIEF: A beginner-friendly MicroPython module for driving a 7-segment
#        multiplexed display (used by the Soldered Pomodoro Timer kit).
# LAST UPDATED: 2025-09-16

import machine
import time


class SevenSegmentDisplay:
    """Drive a multiplexed 7-segment display.

    The public API is intentionally small and beginner-friendly:
      - __init__(digit_refresh_hz=70)
      - clear()
      - write(text)
      - set_decimal_point(position, state=True)

    Multiplexing concept (short): we share the 7 segment driver lines
    across multiple digits. Only one digit is enabled at a time; we
    rapidly switch (cycle) through the digits. When done fast enough
    the human eye sees all digits lit simultaneously.
    """

    # Logical signal levels for the particular PCB wiring used in the kit.
    # SEGMENT_ON: output level that lights a single segment pin
    # DIGIT_ON: output level that enables (selects) a digit common pin
    SEGMENT_ON = 1
    SEGMENT_OFF = 0
    DIGIT_ON = 0   # digits are *active low* on the kit (0 = selected)
    DIGIT_OFF = 1

    # Backwards-compatible constant names (original code used SEG_ON / DIG_ON)
    SEG_ON = SEGMENT_ON
    SEG_OFF = SEGMENT_OFF
    DIG_ON = DIGIT_ON
    DIG_OFF = DIGIT_OFF

    # Segment order used throughout this module: index 0..6 corresponds to
    # segments a, b, c, d, e, f, g respectively.
    # ASCII diagram of a 7-segment display and label names:
    #
    #      -- a --
    #     |       |
    #     f       b
    #     |       |
    #      -- g --
    #     |       |
    #     e       c
    #     |       |
    #      -- d --
    #
    # All patterns below follow the order: [a, b, c, d, e, f, g]

    def __init__(self, digit_refresh_hz=70):
        """Create a SevenSegmentDisplay instance.

        Args:
            digit_refresh_hz (int): How many times per second *each digit*
                should be refreshed (lit). The timer frequency used by
                the driver is `digit_refresh_hz * number_of_digits` and
                must not be changed here if you want the same visible
                behavior as the kit. Default 70Hz per digit is a good
                balance between smoothness and CPU interrupts for a 4-digit
                display.

        Hardware pin mapping (kit):
            segments: pins [2,3,4,5,6,7,8]  # a,b,c,d,e,f,g
            decimal point: pin 9
            digit commons: pins [10,11,12,13]  # digit0 .. digit3

        NOTE: Adjust these pin lists to match your wiring if necessary.
        """

        # --- Pin numbers: change here if your wiring is different ---
        segment_pin_numbers = [2, 3, 4, 5, 6, 7, 8]  # a,b,c,d,e,f,g
        digit_pin_numbers = [10, 11, 12, 13]         # digit 0..3
        dp_pin_number = 9                            # decimal point

        # Create machine.Pin objects for the 7 segments and for the digit selects
        self.segments = [machine.Pin(n, machine.Pin.OUT) for n in segment_pin_numbers]
        self.digits = [machine.Pin(n, machine.Pin.OUT) for n in digit_pin_numbers]
        self.dp = machine.Pin(dp_pin_number, machine.Pin.OUT)

        # Character -> segment pattern mapping. Tuples used to avoid
        # accidental modification and reduce allocations in the IRQ.
        # Order is [a,b,c,d,e,f,g]
        self.patterns = {
            '0': (1, 1, 1, 1, 1, 1, 0), '1': (0, 1, 1, 0, 0, 0, 0),
            '2': (1, 1, 0, 1, 1, 0, 1), '3': (1, 1, 1, 1, 0, 0, 1),
            '4': (0, 1, 1, 0, 0, 1, 1), '5': (1, 0, 1, 1, 0, 1, 1),
            '6': (1, 0, 1, 1, 1, 1, 1), '7': (1, 1, 1, 0, 0, 0, 0),
            '8': (1, 1, 1, 1, 1, 1, 1), '9': (1, 1, 1, 1, 0, 1, 1),
            '-': (0, 0, 0, 0, 0, 0, 1), ' ': (0, 0, 0, 0, 0, 0, 0),
            'A': (1, 1, 1, 0, 1, 1, 1), 'B': (0, 0, 1, 1, 1, 1, 1),
            'C': (1, 0, 0, 1, 1, 1, 0), 'D': (0, 1, 1, 1, 1, 0, 1),
            'E': (1, 0, 0, 1, 1, 1, 1), 'F': (1, 0, 0, 0, 1, 1, 1)
        }

        # Display buffer (one character per digit) and a mask for decimal points
        self.buffer = [" "] * len(self.digits)
        self.dotmask = [False] * len(self.digits)

        # Index of the digit that will be updated next by the timer callback
        self.current_digit = 0

        # ---------------- Timer / refresh explanation ----------------
        # The visible refresh behavior is controlled by this formula:
        #
        #   total_hz = digit_refresh_hz * number_of_digits
        #
        # - `digit_refresh_hz` is how many times per second *each digit* is
        #   refreshed (lit). For example 70Hz means each digit is lit 70
        #   times per second. 
        # - The Timer interrupt needs to fire once per digit each cycle, so
        #   we multiply by the number of digits to get the total timer
        #   frequency. For 4 digits and digit_refresh_hz=70 we get 280Hz.
        # -----------------------------------------------------------------

        total_hz = digit_refresh_hz * len(self.digits)

        # Make sure all digit enables start in the OFF state (safe startup)
        for d in self.digits:
            d.value(self.DIGIT_OFF)

        # Initialize a periodic timer that calls the _refresh method. We
        # intentionally keep the callback small and fast because it runs in
        # interrupt context on most MicroPython ports.
        self.timer = machine.Timer()
        self.timer.init(freq=total_hz, mode=machine.Timer.PERIODIC, callback=self._refresh)


    # ---------------------- Public helper methods ----------------------
    def clear(self):
        """Clear the display buffer (turns all digits to blank, clears dots)."""
        self.buffer = [" "] * len(self.digits)
        self.dotmask = [False] * len(self.digits)

    def write(self, text):
        """Write a string into the digit buffer.

        If `text` is shorter than the number of digits it is padded on the
        right with spaces. If it is longer it will be truncated.

        Example: display.write('12') on a 4-digit display will show '12  '.
        """
        text = str(text)
        if len(text) < len(self.digits):
            text = text + " " * (len(self.digits) - len(text))
        elif len(text) > len(self.digits):
            text = text[:len(self.digits)]
        self.buffer = list(text)

    def set_decimal_point(self, position, state=True):
        """Enable or disable the decimal point on a specific digit.

        Args:
        position (int): digit index (0 = left-most) where to toggle the dot
        state (bool): True to turn the dot on, False to turn it off
        """
        if 0 <= position < len(self.digits):
            self.dotmask[position] = state


    # ---------------------- Internal refresh callback ----------------------
    def _refresh(self, t):
        """Timer callback that updates one digit every call.

        This function is designed to be very small and fast because it is a
        hardware timer callback (interrupt context on some ports). It does the
        following steps in order:
        1) Turn off the previous digit to avoid visual ghosting
        2) Load the character pattern for the current digit from the buffer
        3) Drive the seven segment pins according to that pattern
        4) Set the decimal point pin for this digit
        5) Enable (turn on) the current digit
        6) Advance the index so the next timer tick updates the next digit

        Avoid putting heavy or heap-allocating work here (no long loops,
        no string formatting, no network IO, etc.).
        """

        # Turn off the previously selected digit only (reduces ghosting)
        prev_digit = (self.current_digit - 1) % len(self.digits)
        self.digits[prev_digit].value(self.DIGIT_OFF)

        # Read the character and get its pattern. Use the blank pattern as a
        # safe default (doesn't allocate a new list each time).
        ch = self.buffer[self.current_digit]
        pattern = self.patterns.get(ch, self.patterns[' '])

        # Drive the 7 segment pins for this character
        for i, seg_pin in enumerate(self.segments):
            seg_pin.value(self.SEGMENT_ON if pattern[i] else self.SEGMENT_OFF)

        # Handle the decimal point for this digit
        if self.dp:
            self.dp.value(self.SEGMENT_ON if self.dotmask[self.current_digit] else self.SEGMENT_OFF)

        # Finally, enable this digit (select it)
        self.digits[self.current_digit].value(self.DIGIT_ON)

        # Move to the next digit for the next interrupt
        self.current_digit = (self.current_digit + 1) % len(self.digits)