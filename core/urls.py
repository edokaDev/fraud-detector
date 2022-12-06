from django.urls import path
from .views import IndexView, DashboardView,TransactionsView, WithdrawalView, DepositView, logout_view

app_name = 'core'

urlpatterns = [
    path('', IndexView.as_view(), name='landing'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('dashboard/transactions', TransactionsView.as_view(), name='transactions'),
    path('dashboard/withdrawal', WithdrawalView.as_view(), name='withdraw'),
    path('dashboard/deposit', DepositView.as_view(), name='deposit'),
]