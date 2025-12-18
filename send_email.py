import os
import smtplib
import ssl
from email.message import EmailMessage

# 1. SETUP: Get secrets from GitHub
api_key = os.environ.get("GOOGLE_API_KEY")
email_sender = os.environ.get("EMAIL_ADDRESS")
email_password = os.environ.get("EMAIL_PASSWORD")

# REPLACE THIS with your actual email to test it
email_receiver = "zmeseldzija@gmail.com" 

def send_email():
    if not email_sender or not email_password:
        print("Error: Secrets not found.")
        return

    subject = "Daily Test Update"
    body = "Hello! This is your daily automated update."

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())
            print("Success! Email sent.")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    send_email()
