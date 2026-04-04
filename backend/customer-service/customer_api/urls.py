from django.urls import path
from .views import CartAddView, CartClearView, CartCreateView, CartGetView, HealthView, ServiceInfoView, CustomerLoginView, CustomerCheckoutView, CatalogSearchView

urlpatterns = [
    path('health', HealthView.as_view(), name='health'),
    path('info', ServiceInfoView.as_view(), name='info'),
    # Backward-compatible alias for older clients.
    path('auth/customer/', CustomerLoginView.as_view(), name='auth-customer-login-alias'),
    path('auth/customer/login', CustomerLoginView.as_view(), name='auth-customer-login'),
    path('catalog/search', CatalogSearchView.as_view(), name='catalog-search'),
    path('customer/checkout', CustomerCheckoutView.as_view(), name='customer-checkout'),
    path('customer/cart/create', CartCreateView.as_view(), name='cart-create'),
    path('customer/cart/add', CartAddView.as_view(), name='cart-add'),
    path('customer/cart/clear', CartClearView.as_view(), name='cart-clear'),
    path('customer/cart', CartGetView.as_view(), name='cart-get-base'),
    path('customer/cart/<str:customer_id>', CartGetView.as_view(), name='cart-get'),
]
