from django.urls import include, path

urlpatterns = [
    path('', include('staff_api.urls')),
]
