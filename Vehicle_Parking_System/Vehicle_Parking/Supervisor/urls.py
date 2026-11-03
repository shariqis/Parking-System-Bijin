from django.urls import path
from . import views

urlpatterns = [
    path('Supervisorhome/', views.Supervisorhome, name='Supervisorhome'),
    path('view_todays_booked_slots/', views.view_todays_booked_slots, name='view_todays_booked_slots'),
    path('bookingHistory/', views.bookingHistory, name='bookingHistory'),
    path('Occupied/<int:pk>/', views.Occupied, name='Occupied'),
    path('NotOccupied/<int:pk>/', views.NotOccupied, name='NotOccupied'),
    path('Payment/<int:pk>/', views.Payment, name='Payment'),
    
    path('admin_view_QRcode_details/', views.admin_view_QRcode_details, name='admin_view_QRcode_details'),

    
]