import random
import smtplib
from email.mime.text import MIMEText

# Store OTPs as { (email, role): otp }
otp_storage = {}

def generate_otp(email, role):
    otp = str(random.randint(100000, 999999))
    otp_storage[(email, role)] = otp

    msg = MIMEText(f"Your RetailShield OTP is: {otp}")
    msg['Subject'] = f"RetailShield Login OTP ({role.title()})"
    msg['From'] = 'akhilpupala@gmail.com'  # Use your Gmail sender
    msg['To'] = email

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            # App password! (must have 2FA enabled in Google)
            server.login('akhilpupala@gmail.com', 'zeak scbe kqzg peiv')
            server.send_message(msg)
        print(f"Sent OTP to {email} for role {role}: {otp}")  # for debugging
        return True
    except Exception as e:
        print("Failed to send OTP:", e)   # will print the exact Gmail SMTP error in your terminal!
        return False

def verify_otp(email, role, user_otp):
    return otp_storage.get((email, role)) == user_otp
