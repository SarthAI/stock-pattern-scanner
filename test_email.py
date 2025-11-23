"""
Email Configuration Test Script
Run this to verify your email settings before deploying
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys


def test_email_config():
    """Test email configuration"""
    print("=" * 60)
    print("Stock Pattern Scanner - Email Configuration Test")
    print("=" * 60)
    print()

    # Get email credentials
    print("Enter your email configuration:")
    print()

    smtp_server = input("SMTP Server [smtp.gmail.com]: ").strip() or "smtp.gmail.com"
    smtp_port = input("SMTP Port [587]: ").strip() or "587"
    smtp_port = int(smtp_port)

    sender_email = input("Sender Email: ").strip()
    if not sender_email:
        print("❌ Sender email is required!")
        return False

    sender_password = input("App Password (16 chars): ").strip()
    if not sender_password:
        print("❌ App password is required!")
        return False

    recipient_email = input("Recipient Email: ").strip()
    if not recipient_email:
        print("❌ Recipient email is required!")
        return False

    print()
    print("-" * 60)
    print("Testing email configuration...")
    print("-" * 60)
    print(f"SMTP Server: {smtp_server}:{smtp_port}")
    print(f"Sender: {sender_email}")
    print(f"Recipient: {recipient_email}")
    print()

    try:
        # Create test message
        msg = MIMEMultipart('alternative')
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = "🧪 Stock Pattern Scanner - Test Email"

        body = """<html>
<head>
<style>
body {{ font-family: Arial, sans-serif; }}
.success {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
.content {{ padding: 20px; }}
</style>
</head>
<body>
<div class="success">
<h1>Email Configuration Successful!</h1>
</div>
<div class="content">
<p>Your Stock Pattern Scanner email configuration is working correctly.</p>
<p><strong>SMTP Server:</strong> {0}</p>
<p><strong>Sender:</strong> {1}</p>
<p><strong>Recipient:</strong> {2}</p>
<hr>
<p>You will receive alerts in this format when patterns are detected.</p>
<p style="color: #666; font-style: italic;">This is a test email from Stock Pattern Scanner.</p>
</div>
</body>
</html>""".format(smtp_server, sender_email, recipient_email)

        html_part = MIMEText(body, 'html')
        msg.attach(html_part)

        # Connect and send
        print("Connecting to SMTP server...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            print("Starting TLS...")
            server.starttls()

            print("Logging in...")
            server.login(sender_email, sender_password)

            print("Sending test email...")
            server.send_message(msg)

        print()
        print("=" * 60)
        print("✅ SUCCESS! Test email sent successfully!")
        print("=" * 60)
        print()
        print("Check your inbox at:", recipient_email)
        print()
        print("If you received the email, your configuration is correct!")
        print("You can now use these settings in the Streamlit app.")
        print()

        # Show secrets.toml format
        print("-" * 60)
        print("Copy this to .streamlit/secrets.toml:")
        print("-" * 60)
        print()
        print(f'SENDER_EMAIL = "{sender_email}"')
        print(f'SENDER_PASSWORD = "{sender_password}"')
        print(f'RECIPIENT_EMAIL = "{recipient_email}"')
        print(f'SMTP_SERVER = "{smtp_server}"')
        print(f'SMTP_PORT = {smtp_port}')
        print()
        print("=" * 60)

        return True

    except smtplib.SMTPAuthenticationError:
        print()
        print("=" * 60)
        print("❌ AUTHENTICATION FAILED!")
        print("=" * 60)
        print()
        print("Possible issues:")
        print("1. Incorrect app password (must be 16 characters)")
        print("2. 2-Factor Authentication not enabled on Gmail")
        print("3. App password not generated correctly")
        print()
        print("Fix:")
        print("1. Go to: https://myaccount.google.com/apppasswords")
        print("2. Create new app password for 'Mail'")
        print("3. Use the 16-character password (format: xxxx xxxx xxxx xxxx)")
        print()
        return False

    except smtplib.SMTPException as e:
        print()
        print("=" * 60)
        print("❌ SMTP ERROR!")
        print("=" * 60)
        print()
        print(f"Error: {e}")
        print()
        print("Possible issues:")
        print("1. Incorrect SMTP server or port")
        print("2. Firewall blocking connection")
        print("3. Network connectivity issues")
        print()
        return False

    except Exception as e:
        print()
        print("=" * 60)
        print("❌ UNEXPECTED ERROR!")
        print("=" * 60)
        print()
        print(f"Error: {e}")
        print()
        return False


if __name__ == "__main__":
    print()
    success = test_email_config()
    print()

    if success:
        sys.exit(0)
    else:
        print("Please fix the errors and try again.")
        print()
        sys.exit(1)
