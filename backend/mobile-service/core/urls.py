from django.urls import include, path

urlpatterns = [
    path('', include('mobile_api.urls')),
]
