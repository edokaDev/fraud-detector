from django.db import models
from django.contrib.auth.models import AbstractUser

import random

from datetime import timedelta, date

# Create your models here.

TXTYPES = (
    ("Deposit", 'Deposit'),
    ('Withdrawal', 'Withdrawal'),
)
CARDTYPES = (
    ("Verve", 'Verve'),
    ('Visa', 'Visa'),
    ('MasterCard', 'MasterCard'),
)


class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.username}"


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_no = models.CharField(max_length=10)
    balance = models.FloatField(default=0.00)

    def __str__(self):
        return self.account_no

    def generate_account_no(self):
        num = f'{random.randrange(1000000000, 1999999999)}'

        if len(Account.objects.filter(account_no=num)) > 0:
            return self.generate_card_no()
        
        return num

    def save(self, *args, **kwargs):
        # set account number
        self.account_no = self.generate_account_no()
        super(Account, self).save(*args, **kwargs)
        


class AtmCard(models.Model):
    pin = models.CharField(max_length=4)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    issued_date = models.DateField(auto_now=True)
    expiry_date = models.DateField()
    is_active = models.BooleanField(default=True)
    number = models.IntegerField()
    type = models.CharField(max_length=10, choices=CARDTYPES, default='MasterCard')

    def generate_card_no(self):
        num = f'{random.randrange(5000000000000000, 5999999999999999)}'

        if len(AtmCard.objects.filter(number=num)) > 0:
            return self.generate_card_no()
        
        return num

    def save(self, *args, **kwargs):
        # set card number
        self.number = self.generate_card_no()
        # set expiry date
        self.expiry_date = date.today() + timedelta(days=(365 * 3))
        super(AtmCard, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.type}"


class Transaction(models.Model):
    card = models.ForeignKey(AtmCard, on_delete=models.CASCADE)
    amount = models.IntegerField()
    time = models.DateTimeField(auto_now=True)
    reference_no = models.CharField(max_length=20)
    tx_type = models.CharField(max_length=10, choices=TXTYPES, default='Withdrawal')
    is_approved = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.reference_no

    def generate_ref(self):
        ref = 'TX-AFD-'
        ref += f'{random.randrange(100000, 199999)}'
        return ref
    
    def save(self, *args, **kwargs):
        self.reference_no = self.generate_ref()
        super(Transaction, self).save(*args, **kwargs)


class VerificationCode(models.Model):
    code = models.CharField(max_length=10)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)


    def __str__(self) -> str:
        return self.code
