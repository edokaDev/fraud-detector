from django.urls import path
from .views import IndexView, DashboardView,TransactionsView, WithdrawalView, DepositView, logout_view, CardsView, WithdrawalVerificationView

app_name = 'core'

urlpatterns = [
    path('', IndexView.as_view(), name='landing'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('transactions/', TransactionsView.as_view(), name='transactions'),
    path('withdrawal/', WithdrawalView.as_view(), name='withdraw'),
    path('deposit/', DepositView.as_view(), name='deposit'),
    path('cards/', CardsView.as_view(), name='cards'),
    path('verification/transaction<int:tx_id>', WithdrawalVerificationView.as_view(), name='verification'),
]