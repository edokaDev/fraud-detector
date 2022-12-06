# sms
from twilio.rest import Client
from dotenv import load_dotenv
import os

# ip address validation
import socket
# from core.models import Transaction # circular import

# verification code generation
import random

import datetime

load_dotenv()


class IpVerification:
    @staticmethod
    def get_user_ip():
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            return ip_address
        except:
            # connection error
            return None
    
    def ip_is_valid(self):
        return True


class TimeVerification:
    @staticmethod
    def time_is_valid(time):
        return True



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
        # account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        # auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        # print(account_sid, auth_token)
        # client = Client(account_sid, auth_token)

        # message = client.messages.create(
        #                             body=f'Your verification code is {self.generate_code()}',
        #                             from_='+15044144941',
        #                             to=number
        #                         )
        pass

    def validate_code(self, code):
        # return code == self.code
        return True

# p = CodeVerification()
# # print(p.generate_code())
# # print(p.validate_code(p.code))
# p.send_code('+2348081721540')