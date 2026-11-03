from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # is_admin = models.BooleanField(default=False)
    # is_staff = models.BooleanField(default=False)
    is_customer = models.IntegerField(default=False) # 1 -> user   , 2-> mall , 3-> staff


  


class ParkingSlot(models.Model):
    mall=models.ForeignKey(User, on_delete=models.CASCADE)
    slot_number = models.CharField(max_length=10, unique=True)
    is_reserved = models.BooleanField(default=False)
    vehicle_type = models.CharField(max_length=20, choices=[('Car', 'Car'), ('Bike', 'Bike')])
    location = models.IntegerField()
    is_occupied = models.IntegerField(default=0) # 0 -> Free   , 1-> booked , 2-> alotted ,3 -> paid

class Rate(models.Model):
    mall=models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle_type = models.CharField(max_length=20, choices=[('Car', 'Car'), ('Bike', 'Bike')])
    rate_per_hour = models.DecimalField(max_digits=6, decimal_places=2)
    rate_per_day = models.DecimalField(max_digits=6, decimal_places=2)

class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE ,related_name="user")    
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
   

class Location(models.Model):
    location=models.CharField(max_length=100)

class Mall(models.Model):
    mall = models.ForeignKey(User, on_delete=models.CASCADE , related_name="mall")    
    loc_id = models.ForeignKey(Location, on_delete=models.CASCADE)    
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0) 
    # lat=models.CharField(max_length=20)
    # lon=models.CharField(max_length=20)
    
class Staff(models.Model):
    staff = models.ForeignKey(User, on_delete=models.CASCADE ,related_name="staff") 
    mall = models.ForeignKey(User, on_delete=models.CASCADE ,related_name="mall_staff")


# AI/ML Models for Occupancy Forecasting and Dynamic Pricing
class OccupancyForecast(models.Model):
    """
    Stores predicted occupancy rates for parking slots
    Used for demand forecasting and peak hour identification
    """
    mall = models.ForeignKey(User, on_delete=models.CASCADE, related_name="occupancy_forecasts")
    vehicle_type = models.CharField(max_length=20, choices=[('Car', 'Car'), ('Bike', 'Bike')])
    
    # Time-based forecasting
    forecast_date = models.DateField()  # Date for which prediction is made
    hour = models.IntegerField()  # Hour of day (0-23)
    
    # Predicted metrics
    predicted_occupancy_rate = models.FloatField()  # 0-1 (0% to 100%)
    predicted_available_slots = models.IntegerField()  # Number of slots predicted to be free
    predicted_booked_slots = models.IntegerField()  # Number of slots predicted to be occupied
    confidence_score = models.FloatField()  # Model confidence (0-1)
    
    # Meta information
    demand_level = models.CharField(
        max_length=20,
        choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High'), ('Peak', 'Peak')],
        default='Medium'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('mall', 'vehicle_type', 'forecast_date', 'hour')
        ordering = ['forecast_date', 'hour']
    
    def __str__(self):
        return f"Forecast for {self.mall.username} - {self.forecast_date} {self.hour}:00 ({self.demand_level})"


class DynamicRate(models.Model):
    """
    AI-determined dynamic rates based on occupancy and demand
    Overrides base rates during peak hours
    """
    mall = models.ForeignKey(User, on_delete=models.CASCADE, related_name="dynamic_rates")
    vehicle_type = models.CharField(max_length=20, choices=[('Car', 'Car'), ('Bike', 'Bike')])
    
    # Time window
    applicable_date = models.DateField()
    start_hour = models.IntegerField()  # Start hour (0-23)
    end_hour = models.IntegerField()    # End hour (0-23)
    
    # Dynamic rates
    base_rate_per_hour = models.DecimalField(max_digits=6, decimal_places=2)
    dynamic_rate_per_hour = models.DecimalField(max_digits=6, decimal_places=2)
    price_multiplier = models.FloatField(default=1.0)  # 1.2 = 20% increase, 0.8 = 20% discount
    
    # Reasoning
    demand_level = models.CharField(
        max_length=20,
        choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High'), ('Peak', 'Peak')],
        default='Medium'
    )
    occupancy_rate = models.FloatField()  # Current occupancy %
    
    # Status
    is_active = models.BooleanField(default=True)
    reason = models.TextField(default='')  # Why was this rate set?
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('mall', 'vehicle_type', 'applicable_date', 'start_hour', 'end_hour')
        ordering = ['applicable_date', 'start_hour']
    
    def __str__(self):
        return f"Dynamic Rate {self.mall.username} - {self.applicable_date} {self.start_hour}:00-{self.end_hour}:00"
    
    def get_discount_percentage(self):
        """Returns discount percentage (negative = price increase)"""
        return (self.price_multiplier - 1.0) * 100


class AIMetrics(models.Model):
    """
    Stores performance metrics of AI models for monitoring
    """
    mall = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ai_metrics")
    
    # Forecast accuracy
    forecast_mape = models.FloatField(default=0.0)  # Mean Absolute Percentage Error
    forecast_rmse = models.FloatField(default=0.0)  # Root Mean Squared Error
    forecast_accuracy = models.FloatField(default=0.0)  # Overall accuracy %
    
    # Pricing performance
    revenue_increase_percentage = models.FloatField(default=0.0)  # % revenue change
    occupancy_change_percentage = models.FloatField(default=0.0)  # % occupancy change
    
    # Data statistics
    data_points_used = models.IntegerField(default=0)
    last_training_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-last_training_date']
    
    def __str__(self):
        return f"AI Metrics for {self.mall.username} - Accuracy: {self.forecast_accuracy}%" 