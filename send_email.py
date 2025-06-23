import smtplib
from email.message import EmailMessage

# Set the sender email, password, and recipient email address
from_email_addr = "3664389762@qq.com"
from_email_pass = "facnmkuxaqqochdf"
to_email_addr = "2646320275@qq.com"

# Create a message object
msg = EmailMessage()

# Set the body of the email
body = "Hello from Raspberry Pi"
msg.set_content(body)

# Set sender and recipient email addresses
msg['From'] = from_email_addr
msg['To'] = to_email_addr

# Set the subject line of the email
msg['Subject'] = 'TEST EMAIL'

# Connect to the SMTP server (edit the SMTP server and port according to your provider)
server = smtplib.SMTP('smtp.qq.com', 587)

# Start TLS encryption (comment out this line if your provider doesn’t use TLS)
server.starttls()

# Login to the SMTP server using your email and app password
server.login(from_email_addr, from_email_pass)

# Send the email
server.send_message(msg)

print('Email sent')

# Disconnect from the SMTP server
server.quit()
