from django.urls import path
from . import views
urlpatterns = [
    path('', views.PaymentListView.as_view(), name='payment-list'),
    path('create', views.PaymentCreateView.as_view(), name='payment-create'),
    path('confirm', views.PaymentConfirmView.as_view(), name='payment-confirm'),
]
