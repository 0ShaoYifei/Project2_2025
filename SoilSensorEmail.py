# Program: Plant Moisture Sensor with Email Notification
# Author: Yifei Shao
# Student Number: W20109989
# Date: 23/6/2025
# Description: sending email with gpio input of moisture sensor in certain time of day

import smtplib
from email.message import EmailMessage
import RPi.GPIO as GPIO
from datetime import datetime
import time
import threading

# ===== Email Configuration =====
FROM_EMAIL = "3664389762@qq.com"  # Your QQ email address
FROM_PASSWORD = "facnmkuxaqqochdf"  # QQ email authorization code
TO_EMAIL = "2646320275@qq.com"  # Recipient's email address
SMTP_SERVER = "smtp.qq.com"  # QQ mail SMTP server
SMTP_PORT = 587  # Standard secure SMTP port

# ===== Moisture Sensor Configuration =====
MOISTURE_PIN = 4  # GPIO4 (BCM numbering)
GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering
GPIO.setup(MOISTURE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Enable internal pull-up

# ===== Schedule Configuration =====
CHECK_TIMES = ["10:00", "12:00", "14:00", "16:00"]  # Scheduled check times (24h format)

# ===== Email Sending Function =====
def send_email():
    try:
        # Read sensor state (HIGH = Dry, LOW = Wet)
        is_dry = GPIO.input(MOISTURE_PIN)
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
        # Configure email message
        msg = EmailMessage()
        msg.set_content(body)
        msg['From'] = FROM_EMAIL
        msg['To'] = TO_EMAIL
        msg['Subject'] = f"Plant Status: {status} - {now.strftime('%m/%d %H:%M')}"

        # Connect to SMTP server with increased timeout
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15) as server:
            server.starttls()  # Enable encryption
            server.login(FROM_EMAIL, FROM_PASSWORD)
            server.send_message(msg)  # Send email
        
        # Success message
        print(f"[{timestamp}] Email sent successfully: {status}")
        
    except smtplib.SMTPServerDisconnected as e:
        # Handle unexpected server disconnection
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] Warning: Server disconnected - email may have been sent")
        
    except Exception as e:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Handle specific QQ SMTP quirk while still sending email
        if "(-1, b'\\x00\\x00\\x00')" in str(e):
            print(f"[{timestamp}] Note: Email sent (ignored QQ SMTP quirk)")
        else:
            # Report genuine errors
            print(f"[{timestamp}] Email sending failed: {str(e)}")

# ===== Scheduler Thread =====
def scheduler_thread():
    print("Scheduler started. Checking at:", ", ".join(CHECK_TIMES))
    while True:
        try:
            current_time = datetime.now().strftime("%H:%M")
            # Check if current time matches any scheduled time
            if current_time in CHECK_TIMES:
                send_email()
                # Prevent duplicate triggers in same minute
                time.sleep(60)
            # Check every 30 seconds
            time.sleep(30)
        except Exception as e:
            print(f"Scheduler error: {str(e)}")
            time.sleep(60)

# ===== Main Program =====
if __name__ == "__main__":
    print("Plant Moisture Monitoring System started...")
    print("Press Ctrl+C to stop program")
    
    # Start scheduler in background thread
    scheduler = threading.Thread(target=scheduler_thread, daemon=True)
    scheduler.start()
    
    try:
        # Keep main thread running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nProgram stopped")
    finally:
        GPIO.cleanup()  # Reset GPIO pins
