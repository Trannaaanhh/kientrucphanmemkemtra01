from django.urls import include, path

urlpatterns = [
    path('', include('gateway_api.urls')),
]
