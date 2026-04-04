from django.urls import include, path

urlpatterns = [
    path('', include('laptop_api.urls')),
]
