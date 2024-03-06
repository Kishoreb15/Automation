import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, body, receiver_email):
  """Sends an email with the specified subject, body, and recipient.

  Args:
      subject (str): The subject of the email.
      body (str): The body of the email in HTML format.
      receiver_email (str): The email address of the recipient.

  Logs:
      INFO: Successful email sending.
      ERROR: Error during email sending.
  """

  sender_email = "kishorekumar.b99@gmail.com"  # Replace with your Gmail email
  receiver_email = "kishoreb@clouddestinations.com"  # Replace with recipient email
  email_password = "bxkn slno vdbz xygl"  # Replace with your Gmail App Password
  smtp_server = "smtp.gmail.com"
  smtp_port = 587

  message = MIMEMultipart()
  message['From'] = sender_email
  message['To'] = receiver_email
  message['Subject'] = subject
  message.attach(MIMEText(body, 'html'))

  try:
    with smtplib.SMTP(smtp_server, smtp_port) as server:
      server.starttls()
      server.login(sender_email, email_password)
      server.sendmail(sender_email, receiver_email, message.as_string())
      logging.info(f"Email sent to {receiver_email} with subject: {subject}")
  except Exception as e:
    logging.error(f"Error sending email: {e}")
