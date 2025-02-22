import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib


def is_valid_email(email):
    regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(regex, email) is not None


def send_email(subject, body, to_email, from_email, smtp_server, smtp_port):
    if not is_valid_email(to_email) or not is_valid_email(from_email):
        raise ValueError("Invalid email address")

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise e
