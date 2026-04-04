from django.urls import path
from .views import (
    HealthView,
    ServiceInfoView,
    PcProductListCreateView,
    PcProductSearchView,
    PcProductUpdateView,
    InventoryCheckView,
    InventoryDeductView,
)

urlpatterns = [
    path('health', HealthView.as_view(), name='health'),
    path('info', ServiceInfoView.as_view(), name='info'),
    path('products', PcProductListCreateView.as_view(), name='products'),
    path('products/search', PcProductSearchView.as_view(), name='product-search'),
    path('products/<str:product_id>', PcProductUpdateView.as_view(), name='product-update'),
    path('inventory/check', InventoryCheckView.as_view(), name='inventory-check'),
    path('inventory/deduct', InventoryDeductView.as_view(), name='inventory-deduct'),
]
