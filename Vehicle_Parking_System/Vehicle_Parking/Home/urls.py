from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('Mall_register/', views.Mall_register, name='Mall_register'),
    path('SignIn_User/', views.SignIn_User, name='SignIn_User'),
    path('', views.about, name='about'),
    path('SignIn_Mall/', views.SignIn_Mall, name='SignIn_Mall'),
    path('SignIn_Supervisor/', views.SignIn_Supervisor, name='SignIn_Supervisor'),
    path('SignIn_Admin/', views.SignIn_Admin, name='SignIn_Admin'),
    path('accounts_logout/',views.accounts_logout,name='accounts_logout'),
    path('service/', views.service, name='service'),
]