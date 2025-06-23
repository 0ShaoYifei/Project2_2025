import RPi.GPIO as GPIO
import time

channel = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN)

print("Soil Moisture Sensor Test (Polling Mode)")
print("Press Ctrl+C to exit")

try:
    while True:
        if GPIO.input(channel):
            print("Dry")
        else:
            print("Wet")
        time.sleep(1)
except KeyboardInterrupt:
    print("\nTest Stopped")
finally:
    GPIO.cleanup()
