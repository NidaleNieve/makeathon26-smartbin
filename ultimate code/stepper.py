from machine import Pin
import time

class Stepper:
    def __init__(self, step_pin=16, dir_pin=17, en_pin=18, full_steps_per_rev=200, microsteps=16):
        self.step = Pin(step_pin, Pin.OUT, value=0)
        self.dirp = Pin(dir_pin, Pin.OUT, value=0)
        self.en = Pin(en_pin, Pin.OUT, value=1)  # Active-low enable
        
        self.steps_per_rev = full_steps_per_rev * microsteps
        self.current_position_steps = 0

    def enable(self, on: bool):
        self.en.value(0 if on else 1)

    def step_pulses(self, n_steps: int, step_delay_us: int = 800):
        for _ in range(n_steps):
            self.step.value(1)
            time.sleep_us(3)
            self.step.value(0)
            time.sleep_us(step_delay_us)

    def move_revs(self, revs: float, direction: int, step_delay_us: int = 800):
        self.dirp.value(1 if direction else 0)
        steps = int(revs * self.steps_per_rev)
        self.step_pulses(steps, step_delay_us)
        
        # Update position tracking
        if direction == 1:
            self.current_position_steps += steps
        else:
            self.current_position_steps -= steps

    def move_to_position(self, target_revs: float, step_delay_us: int = 800):
        target_steps = int(target_revs * self.steps_per_rev)
        steps_to_move = target_steps - self.current_position_steps
        
        if steps_to_move == 0:
            return
            
        direction = 1 if steps_to_move > 0 else 0
        self.dirp.value(1 if direction else 0)
        self.step_pulses(abs(steps_to_move), step_delay_us)
        self.current_position_steps = target_steps

    def reset_position(self, step_delay_us: int = 800):
        self.move_to_position(0, step_delay_us)
