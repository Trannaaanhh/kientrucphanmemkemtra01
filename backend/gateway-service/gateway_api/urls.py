from django.urls import path
from .views import (
    CartAddView,
    CustomerCheckoutView,
    CartCreateView,
    CartGetView,
    CatalogSearchView,
    CustomerLoginView,
    HealthView,
    InventoryCheckProxyView,
    InventoryProxyView,
    OrderProxyView,
    PaymentCreateProxyView,
    PaymentProxyView,
    PcProductView,
    PcProductDetailView,
    PcInventoryCheckView,
    PcInventoryDeductView,
    RootView,
    ServiceInfoView,
    StaffAddProductView,
    StaffImportAssetView,
    StaffLoginView,
    StaffUpdateProductView,
)

urlpatterns = [
    path('', RootView.as_view(), name='root'),
    path('health', HealthView.as_view(), name='health'),
    path('info', ServiceInfoView.as_view(), name='info'),
    # Backward-compatible aliases used by older login forms/clients.
    path('auth/customer/', CustomerLoginView.as_view(), name='auth-customer-login-alias'),
    path('auth/staff/', StaffLoginView.as_view(), name='auth-staff-login-alias'),
    path('auth/customer/login', CustomerLoginView.as_view(), name='auth-customer-login'),
    path('auth/staff/login', StaffLoginView.as_view(), name='auth-staff-login'),
    path('catalog/search', CatalogSearchView.as_view(), name='catalog-search'),
    path('customer/cart/create', CartCreateView.as_view(), name='cart-create'),
    path('customer/cart/add', CartAddView.as_view(), name='cart-add'),
    path('customer/cart', CartGetView.as_view(), name='cart-get'),
    path('customer/checkout', CustomerCheckoutView.as_view(), name='customer-checkout'),
    path('staff/products', StaffAddProductView.as_view(), name='staff-product-add'),
    path('staff/products/<str:product_id>', StaffUpdateProductView.as_view(), name='staff-product-update'),
    path('staff/assets/import', StaffImportAssetView.as_view(), name='staff-asset-import'),
    # PC Service routing
    path('pc/products', PcProductView.as_view(), name='pc-product'),
    path('pc/products/<str:product_id>', PcProductDetailView.as_view(), name='pc-product-detail'),
    path('pc/inventory/check', PcInventoryCheckView.as_view(), name='pc-inventory-check'),
    path('pc/inventory/deduct', PcInventoryDeductView.as_view(), name='pc-inventory-deduct'),
    # Inventory proxy
    path('inventory/', InventoryProxyView.as_view(), name='inventory-list'),
    path('inventory/check', InventoryCheckProxyView.as_view(), name='inventory-check'),
    # Order proxy
    path('orders/', OrderProxyView.as_view(), name='order-list'),
    # Payment proxy
    path('payment/', PaymentProxyView.as_view(), name='payment-list'),
    path('payment/create', PaymentCreateProxyView.as_view(), name='payment-create'),
]
