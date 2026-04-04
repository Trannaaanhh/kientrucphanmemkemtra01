from django.urls import path
from . import views
urlpatterns = [
    path('check', views.InventoryCheckView.as_view(), name='inventory-check'),
    path('deduct', views.InventoryDeductView.as_view(), name='inventory-deduct'),
    path('', views.InventoryListView.as_view(), name='inventory-list'),
    path('<str:product_id>', views.InventoryDetailView.as_view(), name='inventory-detail'),
]
