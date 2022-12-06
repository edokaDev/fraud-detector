from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.shortcuts import render
from django.views import View
from django.http import HttpResponse

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout

from .models import User, Transaction

# verifications
from utils.verification import IpVerification, CodeVerification, TimeVerification
from utils.face_detection import DetectFace

class IndexView(View):
    def get(self, request):
        title = 'Welcome'

        context = {
            'title': title,
        }
        # return HttpResponse("Home Page")
        return render(request, 'landing.html', context)

    def post(self, request):
        if 'login' in request.POST:
            context = {}
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('core:dashboard')
            else:
                context['error'] = 'Invalid Credentials, try again!'
            return render(request, 'landing.html', context)

        if 'register' in request.POST:
            balance = request.POST['balance']
            username = request.POST['email']
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            password = request.POST['password']

            new_user = User(
                username=username,
                first_name=first_name,
                last_name=last_name,
                balance=balance,
            )
            new_user.set_password(password)
            new_user.save()
            
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
            return redirect('core:dashboard')




def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return HttpResponseRedirect(reverse('core:landing'))


class DashboardView(LoginRequiredMixin, View):
    login_url = '/'
    redirect_field_name = '/'

    def get(self, request):
        title = 'Dashboard'
        transactions = Transaction.objects.filter(user=request.user)
        tx_count = transactions.count()
        fraud_count = transactions.filter(is_fraud=True).count()

        context = {
            'title': title,
            'tx_count': tx_count,
            'fraud_count': fraud_count,
            'transactions': transactions.order_by('-time')[:5],
        }
        return render(request, 'dashboard.html', context)

    def post(self, request):
        return HttpResponse("Dashboard: post")


class TransactionsView(LoginRequiredMixin, View):
    login_url = '/'
    redirect_field_name = '/'

    def get(self, request):
        title = 'Transactions'
        transactions = Transaction.objects.filter(user=request.user)

        context = {
            'title': title,
            'transactions': transactions.order_by('-time'),
        }
        return render(request, 'transactions.html', context)

    def post(self, request):
        return HttpResponse("Transactions: post")


class WithdrawalView(LoginRequiredMixin, View):
    login_url = '/'
    redirect_field_name = '/'

    def get(self, request):
        title = 'Withdrawal'

        context = {
            'title': title,
        }
        # return HttpResponse("Home Page")
        return render(request, 'withdrawal.html', context)

    def post(self, request):
        ipv = IpVerification()
        ip_valid = ipv.ip_is_valid()

        if ip_valid:
            dface = DetectFace()
            face_valid = dface.face_valid()

            if face_valid:
                amount = request.POST['amount']

                if float(amount) <= request.user.balance:
                    # save the transaction
                    tx = Transaction()
                    tx.amount = amount
                    tx.user = request.user

                    user_max = Transaction.objects.filter(user=request.user).order_by('-amount').first()
                    
                    if float(amount) <= user_max.amount and TimeVerification.time_is_valid(datetime.now()):
                        # appoved
                        # debit user
                        user = request.user
                        user.balance -= float(amount)
                        user.save()
                        tx.save()
                        return HttpResponseRedirect(reverse('core:dashboard'))
                    
                    # Transaction suspicious
                    # send code
                    code = CodeVerification()
                    code.send_code(request.user.phone)
                    
                    if code.validate_code('code'):
                        # appoved
                        # debit user
                        user = request.user
                        user.balance -= float(amount)
                        user.save()
                        tx.save()
                        return HttpResponseRedirect(reverse('core:dashboard'))

                    # Code not correct
                    tx.is_fraud = True
                    tx.save()

        # Error in Transaction
            # amount > user's balance
            # or face is not valid
            # of user ip flags
        return HttpResponseRedirect(reverse('core:dashboard'))

class DepositView(LoginRequiredMixin, View):
    login_url = '/'
    redirect_field_name = '/'

    def get(self, request):
        title = 'Deposit'

        context = {
            'title': title,
        }
        return render(request, 'deposit.html', context)

    def post(self, request):
        amount = request.POST['amount']

        tx = Transaction()
        tx.amount = amount
        tx.user = request.user
        tx.tx_type = 'Deposit'
        tx.save()

        # credit user
        user = request.user
        user.balance += float(amount)
        user.save()

        return HttpResponseRedirect(reverse('core:dashboard'))
