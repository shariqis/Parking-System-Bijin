"""
Dynamic Pricing Module
Calculates optimal rates based on demand forecasting and occupancy
Maximizes revenue while maintaining competitive pricing
"""

from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone
from Admin.models import (
    Rate, DynamicRate, OccupancyForecast, 
    ParkingSlot, AIMetrics, User
)
from User.models import Booking
import logging
import numpy as np

logger = logging.getLogger(__name__)


class DynamicPricingEngine:
    """
    Calculates optimal parking rates based on AI predictions
    Uses demand forecasting to adjust prices dynamically
    """
    
    # Pricing strategy parameters
    PEAK_MULTIPLIER = 1.25      # 25% increase during peak hours
    HIGH_MULTIPLIER = 1.15      # 15% increase during high demand
    MEDIUM_MULTIPLIER = 1.0     # Base rate for medium demand
    LOW_MULTIPLIER = 0.80       # 20% discount for low demand
    
    # Revenue optimization parameters
    MIN_MULTIPLIER = 0.70       # Lowest discount (max 30% off)
    MAX_MULTIPLIER = 1.50       # Highest surge (max 50% premium)
    
    def __init__(self, mall_id):
        """
        Initialize dynamic pricing engine for a mall
        
        Args:
            mall_id: User ID of the mall
        """
        self.mall_id = mall_id
        self.mall = User.objects.get(id=mall_id)
        self.base_rates = self._get_base_rates()
    
    def _get_base_rates(self):
        """Get base rates for all vehicle types"""
        rates = {}
        for rate in Rate.objects.filter(mall_id=self.mall_id):
            rates[rate.vehicle_type] = {
                'hourly': rate.rate_per_hour,
                'daily': rate.rate_per_day
            }
        return rates
    
    def calculate_multiplier_by_demand(self, occupancy_rate):
        """
        Calculate price multiplier based on occupancy rate
        Uses dynamic adjustment for revenue optimization
        
        Args:
            occupancy_rate: Float between 0 and 1
            
        Returns:
            Float: Price multiplier
        """
        if occupancy_rate < 0.3:
            # Low demand - maximum discount to attract customers
            return self.LOW_MULTIPLIER
        elif occupancy_rate < 0.6:
            # Medium demand - base rate
            return self.MEDIUM_MULTIPLIER
        elif occupancy_rate < 0.85:
            # High demand - slight premium
            return self.HIGH_MULTIPLIER
        else:
            # Peak demand - maximum premium
            return self.PEAK_MULTIPLIER
    
    def calculate_optimal_multiplier(self, occupancy_rate, booking_velocity=None):
        """
        Calculate optimal multiplier using advanced strategy
        Considers booking velocity and occupancy trends
        
        Args:
            occupancy_rate: Current/predicted occupancy (0-1)
            booking_velocity: Rate of bookings per hour (optional)
            
        Returns:
            Float: Optimized multiplier
        """
        base_multiplier = self.calculate_multiplier_by_demand(occupancy_rate)
        
        # Adjust based on booking velocity if available
        if booking_velocity:
            # If bookings are accelerating, increase multiplier further
            if booking_velocity > 0.1:  # High booking rate
                base_multiplier = min(self.MAX_MULTIPLIER, base_multiplier * 1.1)
            elif booking_velocity < 0.02:  # Low booking rate
                base_multiplier = max(self.MIN_MULTIPLIER, base_multiplier * 0.95)
        
        return round(base_multiplier, 2)
    
    def generate_dynamic_rates(self, target_date, vehicle_types=['Car', 'Bike']):
        """
        Generate dynamic rates for a specific date based on forecasts
        
        Args:
            target_date: Date object
            vehicle_types: List of vehicle types
            
        Returns:
            List of DynamicRate objects
        """
        dynamic_rates = []
        
        for vehicle_type in vehicle_types:
            # Get forecasts for the day
            forecasts = OccupancyForecast.objects.filter(
                mall_id=self.mall_id,
                vehicle_type=vehicle_type,
                forecast_date=target_date
            ).order_by('hour')
            
            if not forecasts.exists():
                logger.warning(f"No forecasts found for {vehicle_type} on {target_date}")
                continue
            
            # Get base rate
            base_rate = self.base_rates.get(vehicle_type, {}).get('hourly', Decimal('50'))
            
            # Group hours by demand patterns
            hour_groups = self._group_hours_by_demand(forecasts)
            
            for start_hour, end_hour, avg_occupancy, avg_demand in hour_groups:
                # Calculate multiplier
                multiplier = self.calculate_optimal_multiplier(avg_occupancy)
                dynamic_rate = Decimal(str(base_rate)) * Decimal(str(multiplier))
                
                # Create DynamicRate
                rate = DynamicRate(
                    mall_id=self.mall_id,
                    vehicle_type=vehicle_type,
                    applicable_date=target_date,
                    start_hour=start_hour,
                    end_hour=end_hour,
                    base_rate_per_hour=base_rate,
                    dynamic_rate_per_hour=dynamic_rate,
                    price_multiplier=multiplier,
                    demand_level=avg_demand,
                    occupancy_rate=round(avg_occupancy * 100, 2),
                    reason=self._generate_pricing_reason(
                        avg_demand, avg_occupancy, multiplier
                    )
                )
                dynamic_rates.append(rate)
        
        return dynamic_rates
    
    def _group_hours_by_demand(self, forecasts, group_size=2):
        """
        Group consecutive hours by similar demand patterns
        Reduces rate fragmentation
        
        Args:
            forecasts: QuerySet of OccupancyForecast
            group_size: Hours to group together (default 2)
            
        Returns:
            List of tuples (start_hour, end_hour, avg_occupancy, avg_demand)
        """
        groups = []
        i = 0
        
        while i < 24:
            group_forecasts = list(forecasts.filter(
                hour__gte=i, 
                hour__lt=min(i + group_size, 24)
            ))
            
            if not group_forecasts:
                i += group_size
                continue
            
            start_hour = group_forecasts[0].hour
            end_hour = group_forecasts[-1].hour + 1
            
            avg_occupancy = np.mean([f.predicted_occupancy_rate for f in group_forecasts])
            avg_demand = group_forecasts[0].demand_level
            
            groups.append((start_hour, end_hour, avg_occupancy, avg_demand))
            
            i += group_size
        
        return groups
    
    def _generate_pricing_reason(self, demand_level, occupancy_rate, multiplier):
        """Generate human-readable reason for pricing decision"""
        occupancy_pct = round(occupancy_rate * 100, 1)
        change_pct = round((multiplier - 1.0) * 100, 1)
        
        if multiplier > 1.0:
            return f"{demand_level} demand ({occupancy_pct}% occupancy) - Price increased by {change_pct}%"
        elif multiplier < 1.0:
            return f"{demand_level} demand ({occupancy_pct}% occupancy) - Discount of {abs(change_pct)}%"
        else:
            return f"{demand_level} demand ({occupancy_pct}% occupancy) - Base rate applied"
    
    def save_dynamic_rates(self, target_date, vehicle_types=['Car', 'Bike']):
        """
        Generate and save dynamic rates for a date
        
        Args:
            target_date: Date object
            vehicle_types: List of vehicle types
            
        Returns:
            Number of rates created
        """
        try:
            # Delete existing dynamic rates for this date
            DynamicRate.objects.filter(
                mall_id=self.mall_id,
                applicable_date=target_date
            ).delete()
            
            # Generate new rates
            rates = self.generate_dynamic_rates(target_date, vehicle_types)
            
            # Bulk create
            DynamicRate.objects.bulk_create(rates)
            
            logger.info(f"Created {len(rates)} dynamic rates for {self.mall.username} on {target_date}")
            return len(rates)
            
        except Exception as e:
            logger.error(f"Error saving dynamic rates: {str(e)}")
            return 0
    
    def get_active_rate(self, vehicle_type, current_time=None):
        """
        Get current active dynamic rate for a vehicle type
        
        Args:
            vehicle_type: 'Car' or 'Bike'
            current_time: DateTime object (default: now)
            
        Returns:
            DynamicRate object or None
        """
        if current_time is None:
            current_time = timezone.now()
        
        current_hour = current_time.hour
        current_date = current_time.date()
        
        rate = DynamicRate.objects.filter(
            mall_id=self.mall_id,
            vehicle_type=vehicle_type,
            applicable_date=current_date,
            start_hour__lte=current_hour,
            end_hour__gt=current_hour,
            is_active=True
        ).first()
        
        return rate
    
    def get_forecast_rates(self, vehicle_type, target_date):
        """
        Get all dynamic rates for a specific date
        
        Args:
            vehicle_type: 'Car' or 'Bike'
            target_date: Date object
            
        Returns:
            QuerySet of DynamicRate
        """
        return DynamicRate.objects.filter(
            mall_id=self.mall_id,
            vehicle_type=vehicle_type,
            applicable_date=target_date,
            is_active=True
        ).order_by('start_hour')
    
    def get_discount_hours(self, vehicle_type, target_date):
        """
        Get hours with discounted pricing
        
        Args:
            vehicle_type: 'Car' or 'Bike'
            target_date: Date object
            
        Returns:
            List of hour ranges with discounts
        """
        rates = self.get_forecast_rates(vehicle_type, target_date)
        discount_hours = []
        
        for rate in rates:
            if rate.price_multiplier < 1.0:
                discount_hours.append({
                    'start_hour': rate.start_hour,
                    'end_hour': rate.end_hour,
                    'discount_percentage': abs(rate.get_discount_percentage()),
                    'dynamic_rate': float(rate.dynamic_rate_per_hour)
                })
        
        return discount_hours
    
    def get_peak_rate_hours(self, vehicle_type, target_date):
        """
        Get hours with surge pricing
        
        Args:
            vehicle_type: 'Car' or 'Bike'
            target_date: Date object
            
        Returns:
            List of hour ranges with price increases
        """
        rates = self.get_forecast_rates(vehicle_type, target_date)
        peak_hours = []
        
        for rate in rates:
            if rate.price_multiplier > 1.0:
                peak_hours.append({
                    'start_hour': rate.start_hour,
                    'end_hour': rate.end_hour,
                    'surge_percentage': rate.get_discount_percentage(),
                    'dynamic_rate': float(rate.dynamic_rate_per_hour)
                })
        
        return peak_hours
    
    def calculate_revenue_impact(self, target_date):
        """
        Estimate revenue impact of dynamic pricing
        
        Args:
            target_date: Date object
            
        Returns:
            Dictionary with revenue metrics
        """
        dynamic_rates = DynamicRate.objects.filter(
            mall_id=self.mall_id,
            applicable_date=target_date
        )
        
        total_base_revenue = sum(
            float(rate.base_rate_per_hour) * 24 
            for rate in dynamic_rates
        )
        
        total_dynamic_revenue = sum(
            float(rate.dynamic_rate_per_hour) * 24 
            for rate in dynamic_rates
        )
        
        revenue_increase = total_dynamic_revenue - total_base_revenue
        revenue_increase_pct = (revenue_increase / total_base_revenue * 100) if total_base_revenue > 0 else 0
        
        return {
            'estimated_base_revenue': round(total_base_revenue, 2),
            'estimated_dynamic_revenue': round(total_dynamic_revenue, 2),
            'estimated_increase': round(revenue_increase, 2),
            'increase_percentage': round(revenue_increase_pct, 2)
        }


def run_dynamic_pricing_for_mall(mall_id, days_ahead=7):
    """
    Run dynamic pricing calculation for a mall
    
    Args:
        mall_id: User ID of mall
        days_ahead: Number of days to calculate pricing
    """
    engine = DynamicPricingEngine(mall_id)
    
    for day_offset in range(days_ahead):
        target_date = (timezone.now() + timedelta(days=day_offset)).date()
        try:
            engine.save_dynamic_rates(target_date)
        except Exception as e:
            logger.error(f"Failed to generate dynamic pricing for {target_date}: {str(e)}")


def run_all_malls_dynamic_pricing(days_ahead=7):
    """
    Run dynamic pricing for all active malls
    
    Args:
        days_ahead: Number of days to calculate pricing
    """
    malls = User.objects.filter(is_customer=2, is_active=True)
    
    for mall in malls:
        try:
            run_dynamic_pricing_for_mall(mall.id, days_ahead)
            logger.info(f"Completed dynamic pricing for mall: {mall.username}")
        except Exception as e:
            logger.error(f"Error calculating dynamic pricing for {mall.username}: {str(e)}")
