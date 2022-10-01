from twilio.rest import Client
import os

account_sid = os.environ["VG_TWILIO_SID"]
auth_token = os.environ["VG_TWILIO_TOKEN"]

# Send the decrypted authentication code for the 2FA
def send_authentication_code(to_phone, code):
    try:
        client = Client(account_sid, auth_token)

        message = client.messages.create(  
                            messaging_service_sid='MG04d4afcf460e0aee6753136c1c6d2c5d', 
                            body=f'Hello, your two-factor authentication code on VisionGallery is: {code}',
                            to=to_phone
                        )

        return True
    except Exception as e:
        return False
