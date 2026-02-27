from machine import Pin, PWM
import time

class Servo:
    def __init__(self, pin, freq=50, min_us=500, max_us=2500):
        self.pwm = PWM(pin, freq=freq)
        self.min_us = min_us
        self.max_us = max_us
        self.freq = freq

    def write_angle(self, degrees):
        # Constrain degrees between 0 and 180
        degrees = max(0, min(180, degrees))
        
        # Map degrees to pulse width in microseconds
        pulse_us = self.min_us + (self.max_us - self.min_us) * (degrees / 180.0)
        
        # Convert pulse width to duty cycle (0-1023 for ESP32)
        # Period in us = 1000000 / freq
        period_us = 1000000 / self.freq
        duty = int((pulse_us / period_us) * 1023)
        
        self.pwm.duty(duty)

    def deinit(self):
        self.pwm.deinit()

# Initialize servo on Pin 6 (same as main-draft-esp.py)
servo_pin = Pin(6)
servo = Servo(servo_pin)

def test_angle(angle: int, delay_sec: float = 2.0):
    print(f"Moving servo to {angle} degrees...")
    servo.write_angle(angle)
    time.sleep(delay_sec)

print("Starting Servo Angle Tests")
print("Press Ctrl+C to stop at any time.")
time.sleep(2)

try:
    # Test starting position (Lid closed)
    print("\n--- Testing Lid Closed Position ---")
    test_angle(10, 3.0)
    
    # Test open position (Lid open)
    print("\n--- Testing Lid Open Position ---")
    test_angle(160, 3.0)
    
    # Test middle position (just to see the range)
    print("\n--- Testing Middle Position ---")
    test_angle(90, 3.0)
    
    # Return to closed
    print("\n--- Returning to Closed Position ---")
    test_angle(10, 1.0)
    
    print("\nAll tests completed successfully!")

except KeyboardInterrupt:
    print("\nTest stopped by user.")
finally:
    # Clean up PWM
    servo.deinit()
    print("Servo disabled.")
