from django.urls import path, include
urlpatterns = [
    path('payment/', include('payment_api.urls')),
]
