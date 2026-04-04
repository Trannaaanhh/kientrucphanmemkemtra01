from django.urls import include, path

urlpatterns = [
    path('', include('pc_api.urls')),
]
