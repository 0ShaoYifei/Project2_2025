# Program: Plant Moisture Sensor with Email Notification
# Author: Yifei Shao
# Student Number: W20109989
# Date: 23/6/2025
# Description: perform the sensor test

import RPi.GPIO as GPIO
import time

# GPIO configuration for moisture sensor
channel = 4  # Using GPIO4 (BCM numbering)
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN)  # Set as input pin

print("Soil Moisture Sensor Test (Polling Mode)")
print("Press Ctrl+C to exit")

try:
    while True:
        # Read sensor state (HIGH = Dry, LOW = Wet)
        if GPIO.input(channel):
            print("Dry")
        else:
            print("Wet")
        
        time.sleep(1)  # Check every second
except KeyboardInterrupt:
    print("\nTest Stopped")
finally:
    GPIO.cleanup()  # Reset GPIO configuration
