import smtplib
from email.message import EmailMessage
import RPi.GPIO as GPIO
from datetime import datetime
import schedule
import time

# ===== Email Configuration =====
FROM_EMAIL = "3664389762@qq.com"  # Replace with your QQ email
FROM_PASSWORD = "facnmkuxaqqochdf"  # Replace with QQ email app password
TO_EMAIL = "2646320275@qq.com"  # Replace with recipient email
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 587

# ===== Moisture Sensor Configuration =====
MOISTURE_PIN = 4  # Using GPIO4 (BCM numbering)
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOISTURE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Enable internal pull-up resistor

# ===== Email Sending Function =====
def send_email():
    try:
        # Read sensor status
        # HIGH = Dry (needs watering), LOW = Wet (no watering needed)
        is_dry = GPIO.input(MOISTURE_PIN)
        
        # Create timestamp and status information
        now = datetime.now()
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
        status = "NEEDS watering" if is_dry else "does NOT need watering"
        
        # Create email content
        body = f"""Plant Moisture Status Report
        
Detection Time: {timestamp}
Current Status: {status}

Note: 
  - Dry status indicates watering is needed
  - Wet status indicates normal soil moisture
"""
        msg = EmailMessage()
        msg.set_content(body)
        msg['From'] = FROM_EMAIL
        msg['To'] = TO_EMAIL
        msg['Subject'] = f"Plant Status: {status} - {now.strftime('%m/%d %H:%M')}"

        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(FROM_EMAIL, FROM_PASSWORD)
            server.send_message(msg)
        
        print(f"[{timestamp}] Email sent successfully: {status}")
        
    except Exception as e:
        print(f"[{timestamp}] Email sending failed: {str(e)}")

# ===== Schedule Setup =====
schedule.every().day.at("10:00").do(send_email)  # Every day at 10:00 AM
schedule.every().day.at("12:00").do(send_email)  # Every day at 12:00 PM
schedule.every().day.at("14:00").do(send_email)  # Every day at 14:00 PM
schedule.every().day.at("16:00").do(send_email)  # Every day at 14:00 PM

print("Plant Moisture Monitoring System started...")
print("Scheduled detection times: 10:00, 12:00, 14:00,16:00")
print("Press Ctrl+C to stop program")

# ===== Main Loop =====
try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("\nProgram stopped")
finally:
    GPIO.cleanup()
