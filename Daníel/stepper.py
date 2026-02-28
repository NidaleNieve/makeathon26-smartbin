"""
WARNING: This is an in progress implementation of a stepper motor driver
for ESP32 using RMT and MicroPython.
"""

from machine import Pin  # type: ignore
from time import sleep_ms, sleep_us  # type: ignore
import esp32  # type: ignore


class Stepper:
    def __init__(
        self,
        en_pin: int,
        dir_pin: int,
        step_pin: int,
        ms1_pin: int,
        ms2_pin: int,
        ms3_pin: int,
        microstep: int = 8,
        steps_per_rev_base: int = 200,
        ramp_step: float = 0.5,
        ramp_delay_ms: int = 50,
        min_rps: float = 0.05,
        rmt_ch: int = 0,
        rmt_clkdiv: int = 80,
    ):
        # Pines
        self.en = Pin(en_pin, Pin.OUT)
        self.dir = Pin(dir_pin, Pin.OUT)
        self.step = Pin(step_pin, Pin.OUT)
        self.ms1 = Pin(ms1_pin, Pin.OUT)
        self.ms2 = Pin(ms2_pin, Pin.OUT)
        self.ms3 = Pin(ms3_pin, Pin.OUT)

        # Microstepping
        ms_map = {
            1: (0, 0, 0),
            2: (1, 0, 0),
            4: (0, 1, 0),
            8: (1, 1, 0),
            16: (1, 1, 1),
        }
        ms1_val, ms2_val, ms3_val = ms_map[microstep]
        self.ms1.value(ms1_val)
        self.ms2.value(ms2_val)
        self.ms3.value(ms3_val)
        self.microstep = microstep
        self.steps_per_rev = steps_per_rev_base * microstep
        print(
            f"[DEBUG] Microstep: 1/{microstep}, "
            f"{self.steps_per_rev} pulses/rev"
        )

        # Rampa
        self.ramp_step = ramp_step
        self.ramp_delay_ms = ramp_delay_ms
        self.min_rps = min_rps

        # Estado
        self.current_rps = 0.0
        self.current_pos = 0.0  # grados

        # RMT
        self.r = esp32.RMT(rmt_ch, pin=self.step, clock_div=rmt_clkdiv)

        # Start disabled
        self._enable(False)

    def __del__(self):
        """Clean up resources when the instance is deleted."""
        self._stop_rmt()
        self._enable(False)
        print("[DEBUG] Stepper instance deleted")

    def _enable(self, on: bool):
        self.en.value(0 if on else 1)
        print(f"[DEBUG] Driver {'ENABLED' if on else 'DISABLED'}")

    def _calc_pps(self, rps: float) -> int:
        return int(abs(rps) * self.steps_per_rev)

    def _start_rmt(self, pps: int):
        if pps <= 0:
            return
        period_us = int(1_000_000 / pps)
        half = period_us // 2
        self.r.loop(True)
        self.r.write_pulses([half, half], 1)
        print(f"[DEBUG] RMT start: {pps} pps (period {period_us} µs)")

    def _stop_rmt(self):
        self.r.loop(False)
        self.step.value(0)
        print("[DEBUG] RMT stop")

    def _ramp_to(self, vt: float):
        print(f"[DEBUG] Ramping from {self.current_rps:.2f} to {vt:.2f} rps")
        while abs(self.current_rps - vt) > self.ramp_step:
            self.current_rps += (
                self.ramp_step if self.current_rps < vt else -self.ramp_step
            )
            print(f"[DEBUG]   -> {self.current_rps:.2f} rps")
            self.dir.value(1 if self.current_rps > 0 else 0)
            self._start_rmt(self._calc_pps(self.current_rps))
            sleep_ms(self.ramp_delay_ms)
        self.current_rps = vt
        self.dir.value(1 if vt > 0 else 0)
        self._start_rmt(self._calc_pps(vt))
        print(f"[DEBUG] Ramping complete at {vt:.2f} rps")

    def _ramp_down(self):
        print(f"[DEBUG] Ramping down from {self.current_rps:.2f} to 0")
        while abs(self.current_rps) > 0:
            step = self.ramp_step if self.current_rps > 0 else -self.ramp_step
            self.current_rps -= step
            if abs(self.current_rps) < self.min_rps:
                self.current_rps = 0.0
            print(f"[DEBUG]   -> {self.current_rps:.2f} rps")
            self.dir.value(1 if self.current_rps > 0 else 0)
            self._start_rmt(self._calc_pps(self.current_rps))
            sleep_ms(self.ramp_delay_ms)
        self._stop_rmt()
        print("[DEBUG] Ramp down complete at 0 rps")

    def turn(self, rps: float):
        """
        Turn continuously at `rps`. Applies ramps when changing speed
        or direction.
        """
        if abs(rps) < self.min_rps:
            rps = 0.0
        print(f"[DEBUG] turn({rps:.2f} rps) called")

        # If request to stop:
        if rps == 0.0:
            if self.current_rps != 0.0:
                self._ramp_down()
            self._enable(False)
        else:

            # We will turn at a non-zero speed. Ensure driver is enabled
            self._enable(True)

            if self.current_rps == 0.0:
                # If we are starting from rest, just ramp to the desired speed
                self._ramp_to(rps)

            elif self.current_rps * rps < 0:
                # If we are changing direction (current_rps and rps have
                # different signs):
                self._ramp_down()
                self._ramp_to(rps)

            elif self.current_rps != rps:
                # If we are changing the speed but not the direction:
                self._ramp_to(rps)

            # else:
            # If rps is already the current speed, do nothing

    def pos(self, angle: float, speed_rps: float = 1.0):
        """
        Moves to an absolute position in degrees, with ramps
        when starting/stopping.
        """

        print(f"[DEBUG] pos({angle}°) called")
        delta = angle - self.current_pos
        if abs(delta) < (360 / self.steps_per_rev):
            print("[DEBUG] already at position")
        else:
            # Stop continuous rotation if needed
            if self.current_rps != 0.0:
                self._ramp_down()
                self._enable(False)

            # Direction and steps calculation
            self.dir.value(1 if delta > 0 else 0)
            steps = int(abs(delta) / 360 * self.steps_per_rev)
            pps = self._calc_pps(speed_rps)

            # Soft start to the desired speed
            self._enable(True)
            self._ramp_to(speed_rps)

            # Count steps
            period_us = int(1_000_000 / pps)
            for _ in range(steps):
                self.step.value(1)
                sleep_us(period_us // 2)
                self.step.value(0)
                sleep_us(period_us // 2)
            print(f"[DEBUG] Moved {steps} steps")

            # Ramp down to stop
            self._ramp_down()
            self._enable(False)
            self.current_pos = angle
            print(f"[DEBUG] Position set to {angle}°")


# Example
if __name__ == "__main__":
    motor = Stepper(
        en_pin=5,
        dir_pin=16,
        step_pin=17,
        ms1_pin=27,
        ms2_pin=26,
        ms3_pin=25,
        microstep=8,
    )

    # Turn on the motor at 2 rps and wait for 5 seconds
    # motor.turn(2.0)
    # sleep_ms(5000)

    # Move 45º arround
    while True:
        motor.pos(45)
        sleep_ms(1000)
        motor.pos(90)
        sleep_ms(1000)
        motor.pos(135)
        sleep_ms(1000)
        motor.pos(180)
        sleep_ms(2000)

    # Move -45º arround
    # motor.pos(-45)
    # sleep_ms(2000)
    # motor.pos(-90)
    # sleep_ms(1000)
    # motor.pos(-135)
    # sleep_ms(1000)
    # motor.pos(-180)
    # sleep_ms(2000)

    # Turn at 1.5 rps for 5 seconds
    # motor.turn(1.5)
    # sleep_ms(5000)

    # Do not forget to disable the motor
    motor._enable(False)