from django.urls import path
from . import views

urlpatterns = [
    path('userhome/', views.userhome, name='userhome'),
    path('available_slots/', views.available_slots, name='available_slots'),
    path('get-malls/', views.get_malls, name='get_malls'),
    path('get-slots/', views.get_slots, name='get_slots'),
    path('book-slot/', views.book_slot, name='book_slot'),
    path('paynow/', views.paynow, name='paynow'),
    path('success/', views.success, name='success'),
    path('my_booking_history/', views.my_booking_history, name='my_booking_history'),
    path('upcomming_booking/', views.upcomming_booking, name='upcomming_booking'),
    path('Cancel_Booking/<int:pk>/', views.Cancel_Booking, name='Cancel_Booking'),
    path('map_booking/', views.map_booking, name='map_booking'),
]