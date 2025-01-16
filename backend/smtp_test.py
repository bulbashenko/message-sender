import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables
load_dotenv()


def test_email():
    """
    Test email sending using Gmail SMTP
    """
    # Get configuration from environment
    smtp_user = os.getenv("EMAIL_HOST_USER")
    smtp_password = os.getenv("EMAIL_HOST_PASSWORD")

    if not all([smtp_user, smtp_password]):
        print("Error: Missing email configuration. Please check your .env file.")
        return False

    # Create message
    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = smtp_user  # Send test email to yourself
    msg["Subject"] = "Test Email from Django App"

    body = """
    Hello!

    This is a test email from your Django application.
    If you're receiving this, your SMTP configuration is working correctly.

    Best regards,
    Your Django App
    """
    msg.attach(MIMEText(body, "plain"))

    try:
        # Connect to Gmail SMTP
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        # Login
        server.login(smtp_user, smtp_password)

        # Send email
        text = msg.as_string()
        server.sendmail(smtp_user, smtp_user, text)
        server.quit()

        print("Success! Test email sent.")
        print(f"Check your inbox: {smtp_user}")
        return True

    except Exception as e:
        print(f"Error: {str(e)}")
        if "Username and Password not accepted" in str(e):
            print("\nTips:")
            print(
                "1. Make sure you've enabled 'Less secure app access' in your Google Account"
            )
            print(
                "2. Or create an App Password if you're using 2-factor authentication"
            )
            print("3. Check that your email and password are correct in .env")
        return False


if __name__ == "__main__":
    print("Testing Email Configuration...")
    test_email()
