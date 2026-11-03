from django.urls import path
from . import views

urlpatterns = [
    path('Mallhome/', views.Mallhome, name='Mallhome'),
    path('transaction_history/', views.transaction_history, name='transaction_history'),
    path('mall_booking_history/', views.mall_booking_history, name='mall_booking_history'),
]