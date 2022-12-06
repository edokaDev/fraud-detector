from django.db import models
from django.contrib.auth.models import AbstractUser

import random
from utils.verification import IpVerification

# Create your models here.

TXTYPES = (
    ("Deposit", 'Deposit'),
    ('Withdrawal', 'Withdrawal'),
)

class User(AbstractUser):
    tx_pin = models.IntegerField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    balance = models.FloatField(default=0.00)

    def __str__(self):
        return f"{self.username}"


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()
    ip_address = models.CharField(max_length=50, blank=True, null=True)
    time = models.DateTimeField(auto_now=True)
    reference_no = models.CharField(max_length=20)
    tx_type = models.CharField(max_length=10, choices=TXTYPES, default='Withdrawal')
    is_fraud = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.reference_no

    def generate_ref(self):
        ref = 'TX-AFD-'
        ref += f'{random.randrange(100000, 199999)}'
        return ref
    
    def save(self, *args, **kwargs):
        self.reference_no = self.generate_ref()
        self.ip_address = IpVerification.get_user_ip()
        super(Transaction, self).save(*args, **kwargs)
