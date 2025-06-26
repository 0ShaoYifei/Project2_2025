# Program: Plant Moisture Sensor with Email Notification
# Author: Yifei Shao
# Student Number: W20109989
# Date: 23/6/2025
# Description: sending email with gpio input of moisture sensor in certain time of day

import smtplib
from email.message import EmailMessage
import RPi.GPIO as GPIO
from datetime import datetime, time as dt_time, timedelta
import time
import threading
import logging

# ===== Configuration =====
# Email settings
FROM_EMAIL = "3664389762@qq.com"
FROM_PASSWORD = "facnmkuxaqqochdf"
TO_EMAIL = "2646320275@qq.com"
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 587

# Sensor settings
MOISTURE_PIN = 4  # GPIO4 (BCM numbering)

# Schedule settings (24-hour format)
CHECK_TIMES = ["10:00", "12:00", "14:00", "16:00"]

# ===== Setup =====
GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering
GPIO.setup(MOISTURE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Enable internal pull-up

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger()

# ===== Email Function =====
def send_email():
    try:
        # Read sensor state (HIGH = Dry, LOW = Wet)
        is_dry = GPIO.input(MOISTURE_PIN)
        status = "NEEDS watering" if is_dry else "does NOT need watering"
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
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
        msg['Subject'] = f"Plant Status: {status} - {datetime.now().strftime('%m/%d %H:%M')}"

        # Connect to SMTP server
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15) as server:
            server.starttls()  # Enable encryption
            server.login(FROM_EMAIL, FROM_PASSWORD)
            server.send_message(msg)  # Send email
        
        logger.info(f"Email sent successfully: {status}")
        
    except smtplib.SMTPServerDisconnected as e:
        # Handle unexpected server disconnection
        logger.warning(f"Server disconnected - email may have been sent: {str(e)}")
        
    except Exception as e:
        # Handle specific QQ SMTP quirk
        if "(-1, b'\\x00\\x00\\x00')" in str(e):
            logger.info("Email sent (ignored QQ SMTP quirk)")
        else:
            logger.error(f"Email sending failed: {str(e)}")

# ===== Precision Scheduler =====
class PrecisionScheduler(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.timers = []
        self.lock = threading.Lock()
        self.running = True
        
    def schedule(self, time_str):
        """Schedule a daily task at exact time"""
        # Convert time string to time object
        target_time = dt_time(*map(int, time_str.split(':')))
        
        # Calculate initial delay
        now = datetime.now()
        target_dt = datetime.combine(now.date(), target_time)
        
        # If time already passed today, schedule for tomorrow
        if target_dt < now:
            target_dt += timedelta(days=1)
            
        initial_delay = (target_dt - now).total_seconds()
        
        # Create and start timer
        timer = threading.Timer(initial_delay, self.execute_task, args=(time_str,))
        timer.start()
        with self.lock:
            self.timers.append(timer)
    
    def execute_task(self, time_str):
        """Execute task and reschedule for next day"""
        if not self.running:
            return
            
        try:
            # Execute the email sending task
            send_email()
        except Exception as e:
            logger.error(f"Task execution failed: {str(e)}")
        
        # Reschedule for next day
        with self.lock:
            timer = threading.Timer(86400, self.execute_task, args=(time_str,))  # 24 hours
            timer.start()
            self.timers.append(timer)
    
    def run(self):
        """Start all scheduled tasks"""
        for t in CHECK_TIMES:
            self.schedule(t)
            logger.info(f"Scheduled daily email at {t}")
    
    def stop(self):
        """Cancel all scheduled tasks"""
        self.running = False
        with self.lock:
            for timer in self.timers:
                timer.cancel()

# ===== Main Program =====
if __name__ == "__main__":
    logger.info("Plant Moisture Monitoring System started")
    logger.info(f"Scheduled times: {', '.join(CHECK_TIMES)}")
    logger.info("Press Ctrl+C to stop program")
    
    try:
        # Create and start precision scheduler
        scheduler = PrecisionScheduler()
        scheduler.start()
        
        # Keep main thread running
        while True:
            time.sleep(3600)  # Sleep for longer intervals
            
    except KeyboardInterrupt:
        logger.info("Program termination requested")
    finally:
        # Clean up resources
        scheduler.stop()
        GPIO.cleanup()
        logger.info("System shutdown complete")
