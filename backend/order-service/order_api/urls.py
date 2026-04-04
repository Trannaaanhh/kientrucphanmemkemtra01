from django.urls import path
from . import views
urlpatterns = [
    path('', views.OrderCreateView.as_view(), name='order-create'),
    path('checkout', views.OrderCheckoutView.as_view(), name='order-checkout'),
    path('<int:pk>', views.OrderDetailView.as_view(), name='order-detail'),
]
