from django.urls import path
from .views import HealthView, MobileProductListCreateView, MobileProductSearchView, MobileProductUpdateView, ServiceInfoView

urlpatterns = [
    path('health', HealthView.as_view(), name='health'),
    path('info', ServiceInfoView.as_view(), name='info'),
    path('products', MobileProductListCreateView.as_view(), name='products'),
    path('products/search', MobileProductSearchView.as_view(), name='product-search'),
    path('products/<str:product_id>', MobileProductUpdateView.as_view(), name='product-update'),
]
