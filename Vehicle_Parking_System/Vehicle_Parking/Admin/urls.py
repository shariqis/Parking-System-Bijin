from django.urls import path
from . import views, ai_views

urlpatterns = [
    path('manage_parking_slots/', views.manage_parking_slots, name='manage_parking_slots'),
    path('view_parking_slots/', views.view_parking_slots, name='view_parking_slots'),
    path('edit-parking-slot/<int:pk>/', views.edit_parking_slot, name='edit_parking_slot'),
    path('delete-parking-slot/<int:pk>/', views.delete_parking_slot, name='delete_parking_slot'),
    
    path('set-parking-rates/', views.set_parking_rates, name='set_parking_rates'),
    path('view-parking-rates/', views.view_parking_rates, name='view_parking_rates'),
    path('edit_parking_rates/<int:pk>/', views.edit_parking_rates, name='edit_parking_rates'),
    path('delete-parking-rates/<int:pk>/', views.delete_parking_rates, name='delete_parking_rates'),
    
    path('pending-users/', views.pending_users, name='pending_users'),
    path('view-users/', views.view_users, name='view_users'),
    path('approve-user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('reject-user/<int:user_id>/', views.reject_user, name='reject_user'),
    
    path('pending-malls/', views.pending_malls, name='pending_malls'),
    path('view-malls/', views.view_malls, name='view_malls'),
    path('approve-mall/<int:user_id>/', views.approve_mall, name='approve_mall'),
    path('reject-mall/<int:user_id>/', views.reject_mall, name='reject_mall'),
    
    path('adminhome/', views.adminhome, name='adminhome'),
    
    path('addSupervisor/', views.addSupervisor, name='addSupervisor'),
    
    path('add_locations/', views.add_locations, name='add_locations'),
    path('view_locations/', views.view_locations, name='view_locations'),
    path('edit_locations/<int:pk>/', views.edit_locations, name='edit_locations'),
    path('delete_locations/<int:pk>/', views.delete_locations, name='delete_locations'),
    
    # AI/ML Endpoints - Occupancy Forecasting
    path('forecast-dashboard/', ai_views.forecast_dashboard, name='forecast_dashboard'),
    path('api/occupancy-forecast/', ai_views.api_occupancy_forecast, name='api_occupancy_forecast'),
    path('api/peak-hours/', ai_views.api_peak_hours, name='api_peak_hours'),
    path('api/demand-prediction/', ai_views.api_demand_prediction, name='api_demand_prediction'),
    
    # AI/ML Endpoints - Dynamic Pricing
    path('pricing-dashboard/', ai_views.pricing_dashboard, name='pricing_dashboard'),
    path('api/dynamic-rates/', ai_views.api_dynamic_rates, name='api_dynamic_rates'),
    path('api/discount-hours/', ai_views.api_discount_hours, name='api_discount_hours'),
    path('api/surge-pricing/', ai_views.api_surge_pricing, name='api_surge_pricing'),
    path('api/revenue-impact/', ai_views.api_revenue_impact, name='api_revenue_impact'),
]