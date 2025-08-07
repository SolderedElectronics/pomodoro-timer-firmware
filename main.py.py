
# main.py
# Pomodoro Timer using 7-segment display, NeoPixel and buttons on RP2040
# Author: Soldered (https://soldered.com)
# License: MIT

import time
import machine
import neopixel
import seven_segment

# ──────────────────────────────────────────────
# Hardware Configuration

# 7-segment display: a-g on GPIO 2-8, DP on 9
SEGMENT_PINS = [2, 3, 4, 5, 6, 7, 8]
DIGIT_PINS   = [10, 11, 12, 13]
DP_PIN = 9

# Buttons (active-low)
btn_up      = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)
btn_down    = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_UP)
btn_confirm = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)

# NeoPixel on GPIO 1
np = neopixel.NeoPixel(machine.Pin(1), 1)
brightness_level = 0.3

# Buzzer on GPIO 0
buzzer = machine.Pin(0, machine.Pin.OUT)

# Display init
display = seven_segment.SevenSegmentDisplay(SEGMENT_PINS, DIGIT_PINS, DP_PIN)

# ──────────────────────────────────────────────
# Utility Functions

def beep(freq=1000, duration=300):
    pwm = machine.PWM(buzzer)
    pwm.freq(freq)
    pwm.duty_u16(32768)
    time.sleep_ms(duration)
    pwm.duty_u16(0)
    pwm.deinit()

def countdown(seconds, paused_flag, led_color_full, led_color_last_min=None):
    color_changed = False

    while seconds >= 0:
        if led_color_last_min and seconds == 60 and not color_changed:
            update_led(led_color_last_min)
            color_changed = True

        m = seconds // 60
        s = seconds % 60
        frame = [str(m // 10), str(m % 10), str(s // 10), str(s % 10)]

        end_time = time.ticks_add(time.ticks_ms(), 1000)

        while time.ticks_diff(end_time, time.ticks_ms()) > 0:
            # ⏯️ Pause toggle check
            if not btn_confirm.value():
                time.sleep_ms(300)
                paused_flag[0] = not paused_flag[0]

            # ⏸️ While paused: blink all digits together
            while paused_flag[0]:
                now = time.ticks_ms()
                blink_on = (now // 500) % 2 == 0  # 500ms toggle

                if not btn_confirm.value():
                    time.sleep_ms(300)
                    paused_flag[0] = False
                    break

                if blink_on:
                    for i in range(4):
                        display.show_char(i, frame[i])
                else:
                    display.clear()

                time.sleep_ms(display.REFRESH_MS)

            # ▶️ If not paused, show digits normally
            for i in range(4):
                display.show_char(i, frame[i])

        seconds -= 1



def set_times():
    study = 25
    rest = 5
    idx = 0
    debounce = 300
    last = time.ticks_ms()

    while idx < 2:
        now = time.ticks_ms()
        frame = [str(study//10), str(study%10), str(rest//10), str(rest%10)]
        blink_on = (now // 500) % 2 == 0

        for i in range(4):
            if (idx == 0 and i < 2 and not blink_on) or (idx == 1 and i >= 2 and not blink_on):
                display.clear()
                display.digits[i].value(display.DIG_ON)
                time.sleep_ms(display.REFRESH_MS)
                display.digits[i].value(display.DIG_OFF)
            else:
                display.show_char(i, frame[i])

        if not btn_up.value() and time.ticks_diff(now, last) > debounce:
            if idx == 0: study = min(study + 5, 95)
            else: rest = min(rest + 5, 95)
            last = now

        if not btn_down.value() and time.ticks_diff(now, last) > debounce:
            if idx == 0: study = max(study - 5, 0)
            else: rest = max(rest - 5, 0)
            last = now

        if not btn_confirm.value() and time.ticks_diff(now, last) > debounce:
            idx += 1
            last = now

    return study * 60, rest * 60

def update_led(color_tuple):
    np[0] = tuple(int(c * brightness_level) for c in color_tuple)
    np.write()

# ──────────────────────────────────────────────
# Main Logic

def main():
    update_led((35, 91, 121))  # Soldered purple
    beep(1000, 150)
    beep(3000, 200)

    study_secs, rest_secs = set_times()
    paused = [False]  # Mutable flag for pause state

    while True:
        # Work session
        update_led((0, 255, 0))  # Green
        beep(1200, 400)
        countdown(
            study_secs, paused,
            led_color_full=(0, 255, 0),        # Green
            led_color_last_min=(255, 255, 0)   # Yellow
        )

        # Rest session
        update_led((255, 0, 0))  # Red
        beep(1500, 400)
        countdown(
            rest_secs, paused,
            led_color_full=(255, 0, 0),        # Red
            led_color_last_min=(255, 255, 0)   # Yellow
        )


# ──────────────────────────────────────────────

if __name__ == "__main__":
    main()

