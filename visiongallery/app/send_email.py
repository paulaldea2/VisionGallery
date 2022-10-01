from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os

email_address = "noreply.visiongallery@gmail.com"
email_password = os.environ["VG_NOREPLY_EMAIL_PASSWORD"]

# Send the decrypted recovery code in case of a forgotten password
def send_recovery_code(to_address, name, code):
    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['Subject'] = "VisionGallery Account Recovery Code"
    body = f"Hello {name},\n\nWe received a request to reset your VisionGallery password.\nEnter the following reset code: {code}\n\nVisionGallery Team"
    msg.attach(MIMEText(body, 'plain'))

    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(email_address, email_password)
        text = msg.as_string()

        s.sendmail(email_address, to_address, text)
        s.quit()

        return True
    except:
        return False
