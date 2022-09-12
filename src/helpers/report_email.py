import ssl
import smtplib
import datetime
from email.message import EmailMessage

def general_msg(*, sender, reciever, password, subject, body):

    em = EmailMessage()
    em["From"] = sender
    em["To"] = reciever
    em["Subject"] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(sender, password)
        smtp.sendmail(sender, reciever, em.as_string())

