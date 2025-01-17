import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

def test_email():
    smtp_user = os.getenv("EMAIL_HOST_USER")
    smtp_password = os.getenv("EMAIL_HOST_PASSWORD")

    if not all([smtp_user, smtp_password]):
        print("Error: Missing email configuration. Please check your .env file.")
        return False

    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = smtp_user
    msg["Subject"] = "Test Email from Django App"

    body = "Hello!"

    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        server.login(smtp_user, smtp_password)

        text = msg.as_string()
        server.sendmail(smtp_user, smtp_user, text)
        server.quit()

        print("Success! Test email sent.")
        print(f"Check your inbox: {smtp_user}")
        return True

    except Exception as e:
        print(f"Error: {str(e)}")
        return False


if __name__ == "__main__":
    print("Testing Email Configuration...")
    test_email()
