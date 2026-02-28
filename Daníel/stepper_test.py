from stepper import Stepper
from time import sleep_ms

# Initialize motor driver
motor = Stepper(
    en_pin=5, dir_pin=16, step_pin=17,
    ms1_pin=27, ms2_pin=26, ms3_pin=25,
    microstep=8       # 1/8-step mode
)

# Continuous rotation at 2 RPS
motor.turn(2.0)
sleep_ms(5000)

# Move to absolute 45°
motor.pos_abs(45)
sleep_ms(1000)

# Move  relative -90°
motor.pos_rel(-90)
sleep_ms(1000)

# Stop motor
motor.turn(0)