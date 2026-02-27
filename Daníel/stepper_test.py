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

def step_pulses(n_steps: int, step_delay_us: int = 2000):
    # step_delay_us controls speed. Larger = slower.
    # Increased to 2000us (2ms) for slow, safe testing
    for _ in range(n_steps):
        step.value(1)
        time.sleep_us(3)
        step.value(0)
        time.sleep_us(step_delay_us)

def move_revs(revs: float, direction: int, step_delay_us: int = 2000):
    dirp.value(1 if direction else 0)
    steps = int(revs * STEPS_PER_REV)
    step_pulses(steps, step_delay_us)

def test_position(name: str, revs: float):
    print(f"\n--- Testing {name} position ({revs} revs) ---")
    enable_driver(True)
    
    print(f"Moving to {name}...")
    move_revs(revs, direction=1)
    
    print("Waiting 3 seconds...")
    time.sleep(3)
    
    print("Returning to start...")
    move_revs(revs, direction=0)
    
    enable_driver(False)
    print("Done.")

# --- TEST SEQUENCE ---
print("Starting Stepper Angle Tests (Slow Mode)")
print("Press Ctrl+C to stop at any time.")
time.sleep(2)

try:
    # Test Waste (0 revs - just to verify it doesn't move)
    test_position("Waste", 0.0)
    time.sleep(2)
    
    # Test Paper (1/4 turn)
    test_position("Paper", 0.25)
    time.sleep(2)
    
    # Test Plastic (1/2 turn)
    test_position("Plastic", 0.5)
    time.sleep(2)
    
    # Test Glass (3/4 turn)
    test_position("Glass", 0.75)
    
    print("\nAll tests completed successfully!")

except KeyboardInterrupt:
    print("\nTest stopped by user.")
    enable_driver(False)
