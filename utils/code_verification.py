from twilio.rest import Client
from dotenv import load_dotenv
import os

import random

load_dotenv()


class CodeVerification:
    def __init__(self):
        self.code = None
    
    def generate_code(self):
        code = ''
        for i in range(6):
            code += chr(random.randrange(ord('A'), ord('Z')))
        self.code = code
        return code

    def send_code(self, number):
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        print(account_sid, auth_token)
        client = Client(account_sid, auth_token)

        message = client.messages.create(
                                    body=f'Your verification code is {self.generate_code()}',
                                    from_='+15044144941',
                                    to=number
                                )

    def validate_code(self, code):
        return code == self.code

p = CodeVerification()
# print(p.generate_code())
# print(p.validate_code(p.code))
p.send_code('+2348081721540')