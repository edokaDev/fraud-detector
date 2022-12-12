from django.contrib import admin
from .models import User, Account, AtmCard, Transaction, VerificationCode

# Register your models here.

admin.site.register(User)
admin.site.register(Transaction)
admin.site.register(Account)
admin.site.register(AtmCard)
admin.site.register(VerificationCode)
