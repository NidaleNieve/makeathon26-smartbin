from machine import Pin
import time

# Pick safe GPIOs (avoid strapping pins like 0, 2, 12, 15 if you can)
STEP_PIN = 16
DIR_PIN  = 17
EN_PIN   = 18  # Optional, but recommended

step = Pin(STEP_PIN, Pin.OUT, value=0)
dirp = Pin(DIR_PIN,  Pin.OUT, value=0)
en   = Pin(EN_PIN,   Pin.OUT, value=1)  # Many drivers: EN is active-low

# Motor/driver settings
FULL_STEPS_PER_REV = 200
MICROSTEPS = 16  # Set to 1 if full-step, 16 if you configured 1/16 microstepping
STEPS_PER_REV = FULL_STEPS_PER_REV * MICROSTEPS

def enable_driver(on: bool):
    # Active-low enable on A4988/DRV8825
    en.value(0 if on else 1)

def step_pulses(n_steps: int, step_delay_us: int = 800):
    # step_delay_us controls speed. Smaller = faster.
    # Keep STEP high a few microseconds to satisfy both A4988 and DRV8825.
    for _ in range(n_steps):
        step.value(1)
        time.sleep_us(3)
        step.value(0)
        time.sleep_us(step_delay_us)

def move_revs(revs: float, direction: int, step_delay_us: int = 800):
    dirp.value(1 if direction else 0)
    steps = int(revs * STEPS_PER_REV)
    step_pulses(steps, step_delay_us)

enable_driver(True)

# 1 rev forward, then 1 rev backward
move_revs(1.0, direction=1, step_delay_us=800)
time.sleep_ms(500)
move_revs(1.0, direction=0, step_delay_us=800)

enable_driver(False)