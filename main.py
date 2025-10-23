# FILE: main.py
# AUTHOR: Štefan Granatir, Josip Šimun Kuči @ Soldered (original)
# BRIEF:    Main Micropython firmware for Soldered Pomodoro Timer Solder Kit.
#           Handles user interaction (buttons), countdown logic, LED colors,
#           buzzer jingles, and 7-segment display updates.
# LAST UPDATED: 2025-09-16

import time
import machine
import _thread
import neopixel
import seven_segment
from buzzer_music import music
from music_options import *

# ──────────────────────────────────────────────
# Hardware Configuration

# Buttons are wired with pull-ups, so they read 1 when not pressed, 0 when pressed
btn_up      = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)
btn_down    = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_UP)
btn_confirm = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
btn_reset   = machine.Pin(23, machine.Pin.IN, machine.Pin.PULL_UP)

# NeoPixel LED on GPIO 1 (only 1 LED is used here)
led = neopixel.NeoPixel(machine.Pin(1), 1)
brightness_level = 0.3  # scale LED brightness so it’s not blinding

# Buzzer on GPIO 0 for playing melodies
buzzer = machine.Pin(0, machine.Pin.OUT)

# 7-segment display driver instance
display = seven_segment.SevenSegmentDisplay()


# ──────────────────────────────────────────────
# Utility Functions

def jingle_selection():
    """Selects what jingle is played at the start, when study mode begins
       and when rest mdoe begins. Jingles can be customized, see file music_options.py
       for more info
    """
    # Three jumpers select which jingle set to load
    jumper1 = machine.Pin(20, machine.Pin.IN, machine.Pin.PULL_DOWN)
    jumper2 = machine.Pin(19, machine.Pin.IN, machine.Pin.PULL_DOWN)
    jumper3 = machine.Pin(18, machine.Pin.IN, machine.Pin.PULL_DOWN)
    
    # Globals store currently chosen jingles
    global intro_jingle, work_jingle, rest_jingle
    
    # Each jumper corresponds to a different set of intro/work/rest melodies
    if jumper1.value()==1:
        intro_jingle = music(intro_jp1, pins=[buzzer], looping=False)
        work_jingle = music(work_jp1, pins=[buzzer], looping=False)
        rest_jingle = music(rest_jp1, pins=[buzzer], looping=False)
    elif jumper2.value()==1:
        intro_jingle = music(intro_jp2, pins=[buzzer], looping=False)
        work_jingle = music(work_jp2, pins=[buzzer], looping=False)
        rest_jingle = music(rest_jp2, pins=[buzzer], looping=False)
    elif jumper3.value()==1:
        intro_jingle = music(intro_jp3, pins=[buzzer], looping=False)
        work_jingle = music(work_jp3, pins=[buzzer], looping=False)
        rest_jingle = music(rest_jp3, pins=[buzzer], looping=False)
    else:
        # Default jingles if no jumper is set
        intro_jingle = music(intro, pins=[buzzer], looping=False)
        work_jingle = music(work, pins=[buzzer], looping=False)
        rest_jingle = music(rest, pins=[buzzer], looping=False)
        

def play_jingle(jingle):
    """Starts a new thread that plays the jingle
    """
    _thread.start_new_thread(_play_jingle_thread, (jingle,) )

def _play_jingle_thread(jingle):
    """Plays the jingle given to it through an argument
    """
    # Tick() advances music playback; returns False when finished
    result = True
    while result:
        result = jingle.tick()
        time.sleep(0.04)  # small delay for timing control
    jingle.restart()  # reset jingle so it can be played again later

def update_led(color_tuple):
    # Scale each color channel by brightness_level and send to NeoPixel
    led[0] = tuple(int(c * brightness_level) for c in color_tuple)
    led.write()


def countdown(seconds, paused_flag, led_color_full, led_color_last_min=None):
    """Counts down the seconds of a given mode and changes the 7-segment display
       to show it
    """
    color_changed = False

    while seconds >= 0:
        # Change LED to last-minute color when only 60s left
        if led_color_last_min and seconds == 60 and not color_changed:
            update_led(led_color_last_min)
            color_changed = True

        # Convert remaining seconds into MM:SS frame string
        m = seconds // 60
        s = seconds % 60
        frame = f"{m:02}{s:02}"   # always 4 chars (MMSS)
        display.write(frame)

        # Align loop so each iteration lasts ~1 second
        end_time = time.ticks_add(time.ticks_ms(), 1000)
        while time.ticks_diff(end_time, time.ticks_ms()) > 0:
            # Poll buttons during the wait

            # Pause toggle
            if not btn_confirm.value():
                time.sleep_ms(300)  # debounce delay
                paused_flag[0] = not paused_flag[0]
                
            # Reset button restarts main()
            if not btn_reset.value():
                main()

            # Handle paused state (digits blink on/off)
            while paused_flag[0]:
                now = time.ticks_ms()
                blink_on = (now // 500) % 2 == 0  # toggle every 500ms

                if not btn_confirm.value():
                    time.sleep_ms(300)
                    paused_flag[0] = False
                    break

                if blink_on:
                    display.write(frame)
                else:
                    display.clear()

                time.sleep_ms(50)  # reduce busy-looping

        seconds -= 1  # move to next second


def set_times():
    # Default Pomodoro: 25 minutes study, 5 minutes rest
    study = 25
    rest = 5
    idx = 0              # 0 = editing study, 1 = editing rest
    debounce = 500       # debounce time in ms
    last = time.ticks_ms()

    while idx < 2:
        now = time.ticks_ms()
        frame = f"{study:02}{rest:02}"  # Display both times side by side
        blink_on = (now // 500) % 2 == 0

        # Blink the currently edited field to show focus
        if (idx == 0 and not blink_on):
            display.write("  " + frame[2:])  # hide study minutes
        elif (idx == 1 and not blink_on):
            display.write(frame[:2] + "  ")  # hide rest minutes
        else:
            display.write(frame)

        # Button handling with debounce
        if not btn_up.value() and time.ticks_diff(now, last) > debounce:
            if idx == 0: study = min(study + 5, 95)  # step in 5 mins
            else: rest = min(rest + 5, 95)
            last = now

        if not btn_down.value() and time.ticks_diff(now, last) > debounce:
            if idx == 0: study = max(study - 5, 0)
            else: rest = max(rest - 5, 0)
            last = now

        if not btn_confirm.value() and time.ticks_diff(now, last) > debounce:
            idx += 1  # move to next field
            last = now

        time.sleep_ms(40)  # small delay to avoid busy-looping

    return study * 60, rest * 60  # return values in seconds


# ──────────────────────────────────────────────
# Main Loop

def main():
    update_led((35, 91, 121))  # Initial LED color = Soldered purple
    
    jingle_selection()          # Choose jingles based on jumpers
    play_jingle(intro_jingle)  # Play intro tune

    study_secs, rest_secs = set_times()  # let user adjust times
    paused = [False]  # list used so value can be mutated inside functions

    while True:
        # Work session
        update_led((0, 255, 0))  # LED = red during study
        play_jingle(work_jingle)
        time.sleep(0.3)
        countdown(
            study_secs, paused,
            led_color_full=(0, 255, 0),        # Red during study
            led_color_last_min=(255, 255, 0)   # Yellow last minute
        )

        # Rest session
        update_led((255, 0, 0))  # LED = Green during rest
        play_jingle(rest_jingle)
        countdown(
            rest_secs, paused,
            led_color_full=(255, 0, 0),        # Green during rest
            led_color_last_min=(255, 255, 0)   # Yellow last minute
        )


if __name__ == "__main__":
    main()  # Run program only if file is executed directly
