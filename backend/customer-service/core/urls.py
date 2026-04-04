from django.urls import include, path

urlpatterns = [
    path('', include('customer_api.urls')),
]
