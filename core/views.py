from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.shortcuts import render
from django.views import View
from django.http import HttpResponse

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout

from .models import User, Trasaction, TxType


# Create your views here.

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
                return redirect('core:landing')
            else:
                context['error'] = 'Invalid Credentials, try again!'
            return render(request, 'landing.html', context)

        if 'register' in request.POST:
            username = request.POST['email']
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            password = request.POST['password']

            new_user = User(
                username=username,
                first_name=first_name,
                last_name=last_name,
            )
            new_user.set_password(password)
            new_user.save()
            
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
            return redirect('core:landing')




def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return HttpResponseRedirect(reverse('core:landing'))


class DashboardView(LoginRequiredMixin, View):
    login_url = '/'
    redirect_field_name = '/'

    def get(self, request):
        title = 'Dashboard'
        transactions = Trasaction.objects.filter(user=request.user)
        tx_count = transactions.count()
        fraud_count = transactions.filter(tx_type__name='fraud').count()

        context = {
            'title': title,
            'tx_count': tx_count,
            'fraud_count': fraud_count,
        }
        # return HttpResponse("Home Page")
        return render(request, 'dashboard.html', context)

    def post(self, request):
        return HttpResponse("Dashboard: post")


class TransactionsView(LoginRequiredMixin, View):
    login_url = '/'
    redirect_field_name = '/'

    def get(self, request):
        title = 'Transactions'

        context = {
            'title': title,
        }
        # return HttpResponse("Home Page")
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
        return HttpResponse("withdrawal: post")

class DepositView(LoginRequiredMixin, View):
    login_url = '/'
    redirect_field_name = '/'

    def get(self, request):
        title = 'Deposit'

        context = {
            'title': title,
        }
        # return HttpResponse("Home Page")
        return render(request, 'deposit.html', context)

    def post(self, request):
        return HttpResponse("Deposit: post")

