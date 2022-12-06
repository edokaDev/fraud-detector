from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

TXTYPES = (
    ("")
)

class User(AbstractUser):
    tx_pin = models.IntegerField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    balance = models.FloatField(default=0.00)

    def __str__(self):
        return f"{self.username}"


class TxType(models.Model):
    name = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name


class Trasaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()
    is_approved = models.BooleanField(default=False)
    ip_address = models.IntegerField()
    time = models.DateTimeField(auto_now=True)
    reference_no = models.CharField(max_length=20)
    tx_type = models.ForeignKey(TxType, on_delete=models.RESTRICT)
    is_fraud = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.reference_no

