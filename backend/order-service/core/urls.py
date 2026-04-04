from django.urls import path, include
urlpatterns = [
    path('orders/', include('order_api.urls')),
]
