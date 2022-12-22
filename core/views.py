from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.shortcuts import render
from django.views import View
from django.http import HttpResponse

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout

from .models import User, Account, AtmCard, Transaction, VerificationCode

# verifications
from utils.verification import CodeVerification, TimeVerification

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
            username = request.POST['email']
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            password = request.POST['password']

            new_user = User(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=username
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
        title = 'Dashboard New'
        transactions = Transaction.objects.filter(card__account__user=request.user, is_approved=True)
        user_cards = AtmCard.objects.filter(account__user=request.user)
        card_count = user_cards.count()
        user_accounts = Account.objects.filter(user=request.user)
        balance = 0
        # balance from all accounts
        for acc in user_accounts:
            balance += acc.balance

        context = {
            'title': title,
            'transactions': transactions.order_by('-time')[:5],
            'balance': balance,
            'card_count': card_count,
            'user_accounts': user_accounts,
            'account': user_accounts.count(),
            'segment': ['dashboard']
        }
        return render(request, 'dashboard.html', context)

    def post(self, request):
        if 'new_atmcard' in request.POST:
            atm = AtmCard()
            atm.pin = request.POST['pin']
            atm.account_id = request.POST['account_id']
            atm.save()
            return HttpResponseRedirect(reverse('core:dashboard'))

        elif 'new_account' in request.POST:
            acc = Account()
            acc.user = request.user
            acc.balance = request.POST['balance']
            acc.save()
            return HttpResponseRedirect(reverse('core:dashboard'))
        return HttpResponseRedirect(reverse('core:landing'))

class TransactionsView(LoginRequiredMixin, View):
    login_url = '/'
    redirect_field_name = '/'

    def get(self, request):
        title = 'Transactions'
        transactions = Transaction.objects.filter(card__account__user=request.user, is_approved=True)

        context = {
            'title': title,
            'transactions': transactions.order_by('-time'),
            'segment': ['all-transactions','transactions']
        }
        return render(request, 'transactions.html', context)

    def post(self, request):
        return HttpResponse("Transactions: post")


class WithdrawalView(LoginRequiredMixin, View):
    login_url = '/'
    redirect_field_name = '/'

    def get(self, request):
        title = 'Withdrawal'
        user_cards = AtmCard.objects.filter(account__user=request.user)

        context = {
            'title': title,
            'segment': ['withdraw', 'transactions'],
            'cards': user_cards
        }
        # return HttpResponse("Home Page")
        return render(request, 'withdrawal.html', context)

    def post(self, request):
        context = {
            'title': 'Withdrawal',
            'segment': ['withdraw', 'transactions'],
            'cards': AtmCard.objects.filter(account__user=request.user),
        }

        if 'withdraw_next' in request.POST:
            card_id = request.POST['card_id']
            pin = request.POST['pin']
            card = AtmCard.objects.get(id=card_id)

            # validate pin
            if pin != card.pin:
                context['error'] = 'Incorrect Pin'
                return render(request, 'withdrawal.html', context)

            amount = request.POST['amount']

            if float(amount) > card.account.balance:
                context['error'] = 'Insufficient Funds'
                return render(request, 'withdrawal.html', context)
            
            else:

                user_max = Transaction.objects.filter(card_id=card_id, tx_type='Withdrawal', is_approved=True).order_by('-amount').first()
                if user_max is not None:
                    # user has previous transactions

                    if float(amount) > user_max.amount or not TimeVerification.time_is_valid(datetime.now()):
                        # time odd or unusual amount
                        # verification required
                        # save the transaction
                        tx = Transaction()
                        tx.card = card
                        tx.amount = amount
                        tx.save()
                        # redirect to verification page
                        context['verification'] = 'verification'
                        return HttpResponseRedirect(reverse('core:verification', args=(tx.id,)))

                # user has no previous transactions
                # or transaction is legit

                # debit account
                account_to_debit = card.account
                account_to_debit.balance -= float(amount)
                account_to_debit.save()

                # save transaction
                tx = Transaction()
                tx.card = card
                tx.amount = amount
                tx.is_approved = True
                tx.save()
        return HttpResponseRedirect(reverse('core:dashboard'))


class WithdrawalVerificationView(LoginRequiredMixin, View):
    login_url = '/'
    redirect_field_name = '/'

    code = None


    def get(self, request, tx_id):
        tx = Transaction.objects.get(id=tx_id)

        title = 'Verification'
        context = {
            'title': title,
            'segment': ['withdrawal', 'transactions'],
            'amount': tx.amount,
            'send_code': True,
        }
        return render(request, 'verification.html', context)

    
    def post(self, request, tx_id):
        title = 'Verification'
        context = {
            'title': title,
            'segment': ['withdrawal', 'transactions'],
        }
        if 'send_sms' in request.POST:
            # generate / send sms code

            code = CodeVerification.generate_code()

            c = VerificationCode()
            c.code = code
            c.transaction_id = tx_id
            c.save()

            # send code to user's phone
            # CodeVerification.send_code(request.user.phone)
            
            print(f"==================\n{code}\n================")

            # redirect user
            context['code_sent'] = True
            return render(request, 'verification.html', context)

        elif 'sms_code' in request.POST:
            input_code = request.POST['sms_code']
            # verify code
            correct_code = VerificationCode.objects.filter(transaction_id=tx_id).first()
            if input_code != correct_code.code:
                # code mismatch
                # block transaction
                context['blocked'] = True
                context['error'] = 'Incorrect Code, Transaction Blocked!'
                return render(request, 'verification.html', context)
            # else 
            # success
            # update transaction
            transaction = Transaction.objects.get(id=tx_id)
            transaction.is_approved = True
            transaction.save()

            # debit user
            acc = transaction.card.account
            acc.balance -= float(transaction.amount)
            acc.save()

            context['approved'] = True

            return render(request, 'verification.html', context)

        return HttpResponseRedirect(reverse('core:dashboard'))




class DepositView(LoginRequiredMixin, View):
    login_url = '/'
    redirect_field_name = '/'

    def get(self, request):
        title = 'Deposit'
        user_accounts = Account.objects.filter(user=request.user)

        context = {
            'title': title,
            'segment': ['deposit', 'transactions'],
            'accounts': user_accounts
        }
        return render(request, 'deposit.html', context)

    def post(self, request):
        amount = request.POST['amount']
        account_id = request.POST['account_id']
        account = Account.objects.get(id=account_id)
        card = AtmCard.objects.filter(account=account).first()

        tx = Transaction()
        tx.amount = amount
        tx.card = card
        tx.tx_type = 'Deposit'
        tx.is_approved = True
        tx.save()

        # credit user
        account.balance += float(amount)
        account.save()

        return HttpResponseRedirect(reverse('core:dashboard'))

class CardsView(LoginRequiredMixin, View):
    login_url = '/'
    redirect_field_name = '/'

    def get(self, request):
        title = 'ATM Cards'
        user_accounts = Account.objects.filter(user=request.user)
        user_cards = AtmCard.objects.filter(account__user=request.user)
        card_count = user_cards.count()
        context = {
            'title': title,
            'segment': ['cards'],
            'cards': user_cards,
            'card_count': card_count,
            'card_types': ['Verve', 'MasterCard', 'Visa'],
            'user_accounts': user_accounts,
        }
        return render(request, 'atm_cards.html', context)
    
    def post(self, request):
        atm = AtmCard()
        atm.type = request.POST['type']
        atm.pin = request.POST['pin']
        atm.account_id = request.POST['account_id']
        atm.save()
        return HttpResponseRedirect(reverse('core:cards'))
