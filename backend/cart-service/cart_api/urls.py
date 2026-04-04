from django.urls import path
from . import views
urlpatterns = [
    path('', views.CartGetView.as_view(), name='cart-get'),
    path('add', views.CartAddView.as_view(), name='cart-add'),
    path('update', views.CartUpdateView.as_view(), name='cart-update'),
    path('remove', views.CartRemoveView.as_view(), name='cart-remove'),
]
