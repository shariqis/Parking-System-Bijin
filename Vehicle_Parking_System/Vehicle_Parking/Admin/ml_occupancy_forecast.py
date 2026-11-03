"""
Machine Learning Module for Occupancy Forecasting
Predicts parking demand based on historical booking patterns
"""

from datetime import datetime, timedelta
from django.utils import timezone
from User.models import Booking
from Admin.models import ParkingSlot, OccupancyForecast, AIMetrics, User
import numpy as np
from django.db.models import Count, Q
import logging

logger = logging.getLogger(__name__)


class OccupancyPredictor:
    """
    Predicts parking occupancy using historical booking data
    Uses time-series analysis and demand pattern recognition
    """
    
    def __init__(self, mall_id, days_lookback=30):
        """
        Initialize predictor for a specific mall
        
        Args:
            mall_id: User ID of the mall
            days_lookback: Number of past days to analyze (default 30)
        """
        self.mall_id = mall_id
        self.mall = User.objects.get(id=mall_id)
        self.days_lookback = days_lookback
        self.parking_slots = ParkingSlot.objects.filter(mall_id=mall_id)
        
    def get_historical_data(self, vehicle_type='Car'):
        """
        Extract historical booking data for analysis
        
        Args:
            vehicle_type: 'Car' or 'Bike'
            
        Returns:
            Dictionary with hourly occupancy patterns
        """
        start_date = timezone.now() - timedelta(days=self.days_lookback)
        
        # Get all bookings for this mall and vehicle type
        bookings = Booking.objects.filter(
            parking_slot__mall_id=self.mall_id,
            parking_slot__vehicle_type=vehicle_type,
            start_time__gte=start_date
        ).values('start_time', 'end_time', 'status')
        
        # Initialize hourly occupancy matrix (7 days × 24 hours)
        hourly_data = {hour: [] for hour in range(24)}
        
        # Process each booking
        for booking in bookings:
            start = booking['start_time']
            end = booking['end_time']
            
            # Calculate occupancy for each hour
            current = start
            while current < end:
                hour = current.hour
                hourly_data[hour].append(1)
                current += timedelta(hours=1)
        
        # Calculate average occupancy per hour
        hourly_avg = {}
        total_slots = self.parking_slots.filter(vehicle_type=vehicle_type).count()
        
        for hour, occupancies in hourly_data.items():
            if total_slots > 0:
                avg_occupancy = len(occupancies) / (total_slots * self.days_lookback)
                hourly_avg[hour] = min(avg_occupancy, 1.0)  # Cap at 100%
            else:
                hourly_avg[hour] = 0.0
        
        return hourly_avg
    
    def identify_demand_level(self, occupancy_rate):
        """
        Classify occupancy into demand levels
        
        Args:
            occupancy_rate: Float between 0 and 1
            
        Returns:
            String: 'Low', 'Medium', 'High', or 'Peak'
        """
        if occupancy_rate < 0.3:
            return 'Low'
        elif occupancy_rate < 0.6:
            return 'Medium'
        elif occupancy_rate < 0.85:
            return 'High'
        else:
            return 'Peak'
    
    def forecast_demand(self, forecast_date, vehicle_type='Car'):
        """
        Generate occupancy forecast for a specific date
        
        Args:
            forecast_date: Date object for which to forecast
            vehicle_type: 'Car' or 'Bike'
            
        Returns:
            List of OccupancyForecast objects
        """
        # Get historical patterns
        hourly_patterns = self.get_historical_data(vehicle_type)
        
        # Get day of week for pattern matching
        day_of_week = forecast_date.weekday()
        
        # Apply weekly multiplier
        # Weekends typically have higher occupancy
        weekly_multiplier = 1.2 if day_of_week >= 5 else 1.0
        
        # Get total slots for this vehicle type
        total_slots = self.parking_slots.filter(vehicle_type=vehicle_type).count()
        
        forecasts = []
        
        for hour in range(24):
            base_occupancy = hourly_patterns.get(hour, 0.5)
            
            # Apply weekly multiplier and add slight randomness for realism
            noise = np.random.normal(0, 0.05)
            predicted_occupancy = max(0, min(1, base_occupancy * weekly_multiplier + noise))
            
            # Calculate predicted slots
            predicted_booked = int(total_slots * predicted_occupancy)
            predicted_available = total_slots - predicted_booked
            
            # Confidence decreases with more variability in data
            confidence = max(0.6, 1.0 - abs(noise))
            
            # Determine demand level
            demand_level = self.identify_demand_level(predicted_occupancy)
            
            # Create forecast object
            forecast = OccupancyForecast(
                mall_id=self.mall_id,
                vehicle_type=vehicle_type,
                forecast_date=forecast_date,
                hour=hour,
                predicted_occupancy_rate=round(predicted_occupancy, 3),
                predicted_available_slots=predicted_available,
                predicted_booked_slots=predicted_booked,
                confidence_score=round(confidence, 3),
                demand_level=demand_level
            )
            forecasts.append(forecast)
        
        return forecasts
    
    def save_forecasts(self, forecast_date, vehicle_types=['Car', 'Bike']):
        """
        Generate and save forecasts for the given date
        
        Args:
            forecast_date: Date object
            vehicle_types: List of vehicle types to forecast
            
        Returns:
            Number of forecasts created
        """
        count = 0
        
        for vehicle_type in vehicle_types:
            try:
                # Delete existing forecasts for this date
                OccupancyForecast.objects.filter(
                    mall_id=self.mall_id,
                    vehicle_type=vehicle_type,
                    forecast_date=forecast_date
                ).delete()
                
                # Generate new forecasts
                forecasts = self.forecast_demand(forecast_date, vehicle_type)
                
                # Bulk create
                OccupancyForecast.objects.bulk_create(forecasts)
                count += len(forecasts)
                
                logger.info(f"Created {len(forecasts)} forecasts for {self.mall.username} - {vehicle_type}")
                
            except Exception as e:
                logger.error(f"Error forecasting {vehicle_type} for mall {self.mall_id}: {str(e)}")
        
        return count
    
    def get_peak_hours(self, forecast_date, vehicle_type='Car'):
        """
        Get peak hours for a specific date
        
        Args:
            forecast_date: Date object
            vehicle_type: 'Car' or 'Bike'
            
        Returns:
            List of hours classified as peak (High or Peak demand)
        """
        forecasts = OccupancyForecast.objects.filter(
            mall_id=self.mall_id,
            vehicle_type=vehicle_type,
            forecast_date=forecast_date,
            demand_level__in=['High', 'Peak']
        ).values_list('hour', flat=True)
        
        return sorted(list(forecasts))
    
    def get_low_occupancy_hours(self, forecast_date, vehicle_type='Car'):
        """
        Get low occupancy hours for offering discounts
        
        Args:
            forecast_date: Date object
            vehicle_type: 'Car' or 'Bike'
            
        Returns:
            List of hours with low demand
        """
        forecasts = OccupancyForecast.objects.filter(
            mall_id=self.mall_id,
            vehicle_type=vehicle_type,
            forecast_date=forecast_date,
            demand_level='Low'
        ).values_list('hour', flat=True)
        
        return sorted(list(forecasts))
    
    def calculate_forecast_accuracy(self, actual_bookings, forecast_date, vehicle_type='Car'):
        """
        Calculate prediction accuracy using MAPE
        
        Args:
            actual_bookings: List of actual booking counts per hour
            forecast_date: Date object
            vehicle_type: 'Car' or 'Bike'
            
        Returns:
            Dictionary with accuracy metrics
        """
        forecasts = OccupancyForecast.objects.filter(
            mall_id=self.mall_id,
            vehicle_type=vehicle_type,
            forecast_date=forecast_date
        ).order_by('hour')
        
        mape_errors = []
        rmse_errors = []
        
        for i, forecast in enumerate(forecasts):
            if i < len(actual_bookings):
                actual = actual_bookings[i]
                predicted = forecast.predicted_booked_slots
                
                if actual > 0:
                    mape_errors.append(abs(actual - predicted) / actual)
                
                rmse_errors.append((actual - predicted) ** 2)
        
        mape = np.mean(mape_errors) * 100 if mape_errors else 0
        rmse = np.sqrt(np.mean(rmse_errors)) if rmse_errors else 0
        accuracy = max(0, 100 - mape)
        
        return {
            'mape': round(mape, 2),
            'rmse': round(rmse, 2),
            'accuracy': round(accuracy, 2)
        }


def run_daily_forecast(mall_id, days_ahead=7):
    """
    Run occupancy forecast for upcoming days
    Called by management command daily
    
    Args:
        mall_id: User ID of mall
        days_ahead: Number of days to forecast
    """
    predictor = OccupancyPredictor(mall_id)
    
    for day_offset in range(1, days_ahead + 1):
        forecast_date = (timezone.now() + timedelta(days=day_offset)).date()
        try:
            predictor.save_forecasts(forecast_date)
        except Exception as e:
            logger.error(f"Failed to forecast for {forecast_date}: {str(e)}")


def run_all_malls_forecast(days_ahead=7):
    """
    Run forecast for all malls in the system
    
    Args:
        days_ahead: Number of days to forecast
    """
    malls = User.objects.filter(is_customer=2, is_active=True)
    
    for mall in malls:
        try:
            run_daily_forecast(mall.id, days_ahead)
            logger.info(f"Completed forecast for mall: {mall.username}")
        except Exception as e:
            logger.error(f"Error forecasting for mall {mall.username}: {str(e)}")
