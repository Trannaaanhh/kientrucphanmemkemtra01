from django.urls import path
from .views import HealthView, LaptopProductListCreateView, LaptopProductSearchView, LaptopProductUpdateView, ServiceInfoView

urlpatterns = [
    path('health', HealthView.as_view(), name='health'),
    path('info', ServiceInfoView.as_view(), name='info'),
    path('products', LaptopProductListCreateView.as_view(), name='products'),
    path('products/search', LaptopProductSearchView.as_view(), name='product-search'),
    path('products/<str:product_id>', LaptopProductUpdateView.as_view(), name='product-update'),
]
