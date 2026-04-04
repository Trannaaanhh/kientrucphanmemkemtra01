from django.urls import path
from .views import HealthView, ServiceInfoView, StaffAuditAddView, StaffAuditListView, StaffAuditUpdateView, StaffLoginView, StaffAddProductView, StaffUpdateProductView, StaffImportAssetView

urlpatterns = [
    path('health', HealthView.as_view(), name='health'),
    path('info', ServiceInfoView.as_view(), name='info'),
    path('staff/audit/add', StaffAuditAddView.as_view(), name='audit-add'),
    path('staff/audit/update', StaffAuditUpdateView.as_view(), name='audit-update'),
    path('staff/audit', StaffAuditListView.as_view(), name='audit-list'),
    # Backward-compatible alias for older clients.
    path('auth/staff/', StaffLoginView.as_view(), name='auth-staff-login-alias'),
    path('auth/staff/login', StaffLoginView.as_view(), name='auth-staff-login'),
    path('staff/products', StaffAddProductView.as_view(), name='staff-product-add'),
    path('staff/products/<str:product_id>', StaffUpdateProductView.as_view(), name='staff-product-update'),
    path('staff/assets/import', StaffImportAssetView.as_view(), name='staff-asset-import'),
]
