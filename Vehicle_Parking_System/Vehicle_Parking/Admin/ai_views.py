"""
Views and APIs for displaying occupancy forecasts and dynamic pricing
Provides data endpoints for mall dashboards
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime, timedelta
from Admin.models import OccupancyForecast, DynamicRate, AIMetrics
import json
import logging

logger = logging.getLogger(__name__)


# ==================== Forecasting Views ====================

@login_required
def forecast_dashboard(request):
    """Display occupancy forecast dashboard for mall admin"""
    mall_id = request.session.get('mall_id')
    if not mall_id:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    today = timezone.now().date()
    
    context = {
        'uname': request.session.get('uname', 'User'),
        'mall_id': mall_id,
        'today': today.isoformat(),
    }
    
    return render(request, 'admin/forecast_dashboard.html', context)


@csrf_exempt
@login_required
def api_occupancy_forecast(request):
    """
    API endpoint to get occupancy forecasts
    Query parameters:
      - date: YYYY-MM-DD format (optional, default today)
      - vehicle_type: 'Car' or 'Bike' (optional, default both)
    """
    mall_id = request.session.get('mall_id')
    if not mall_id:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        date_str = request.GET.get('date', timezone.now().date().isoformat())
        forecast_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        vehicle_type = request.GET.get('vehicle_type', None)
        
        # Query forecasts
        query = OccupancyForecast.objects.filter(
            mall_id=mall_id,
            forecast_date=forecast_date
        )
        
        if vehicle_type:
            query = query.filter(vehicle_type=vehicle_type)
        
        forecasts = query.order_by('hour')
        
        # Format response
        data = {
            'date': forecast_date.isoformat(),
            'mall_id': mall_id,
            'forecasts': [
                {
                    'hour': f.hour,
                    'hour_display': f'{f.hour:02d}:00',
                    'vehicle_type': f.vehicle_type,
                    'occupancy_rate': f.predicted_occupancy_rate,
                    'occupancy_percentage': round(f.predicted_occupancy_rate * 100, 1),
                    'available_slots': f.predicted_available_slots,
                    'booked_slots': f.predicted_booked_slots,
                    'confidence': f.confidence_score,
                    'demand_level': f.demand_level,
                }
                for f in forecasts
            ]
        }
        
        return JsonResponse(data)
        
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    except Exception as e:
        logger.error(f"Error fetching forecasts: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@login_required
def api_peak_hours(request):
    """
    Get peak hours forecast for upcoming days
    Returns hours with High or Peak demand
    """
    mall_id = request.session.get('mall_id')
    if not mall_id:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        vehicle_type = request.GET.get('vehicle_type', 'Car')
        days_ahead = int(request.GET.get('days_ahead', 7))
        
        data = {
            'peak_hours_by_day': []
        }
        
        for day_offset in range(days_ahead):
            date = (timezone.now() + timedelta(days=day_offset)).date()
            
            forecasts = OccupancyForecast.objects.filter(
                mall_id=mall_id,
                vehicle_type=vehicle_type,
                forecast_date=date,
                demand_level__in=['High', 'Peak']
            ).order_by('hour')
            
            hours = [f.hour for f in forecasts]
            
            data['peak_hours_by_day'].append({
                'date': date.isoformat(),
                'peak_hours': hours,
                'peak_count': len(hours)
            })
        
        return JsonResponse(data)
        
    except Exception as e:
        logger.error(f"Error fetching peak hours: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@login_required
def api_demand_prediction(request):
    """
    Get overall demand prediction for specified date range
    Useful for capacity planning
    """
    mall_id = request.session.get('mall_id')
    if not mall_id:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        days_ahead = int(request.GET.get('days_ahead', 7))
        vehicle_type = request.GET.get('vehicle_type', None)
        
        data = {
            'summary_by_date': []
        }
        
        for day_offset in range(days_ahead):
            date = (timezone.now() + timedelta(days=day_offset)).date()
            
            query = OccupancyForecast.objects.filter(
                mall_id=mall_id,
                forecast_date=date
            )
            
            if vehicle_type:
                query = query.filter(vehicle_type=vehicle_type)
            
            forecasts = list(query)
            
            if forecasts:
                avg_occupancy = sum(f.predicted_occupancy_rate for f in forecasts) / len(forecasts)
                peak_demand = max([f.demand_level for f in forecasts], key=lambda x: ['Low', 'Medium', 'High', 'Peak'].index(x))
                
                data['summary_by_date'].append({
                    'date': date.isoformat(),
                    'day_name': date.strftime('%A'),
                    'average_occupancy': round(avg_occupancy, 3),
                    'average_occupancy_pct': round(avg_occupancy * 100, 1),
                    'peak_demand_level': peak_demand,
                    'forecast_count': len(forecasts)
                })
        
        return JsonResponse(data)
        
    except Exception as e:
        logger.error(f"Error fetching demand prediction: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


# ==================== Dynamic Pricing Views ====================

@login_required
def pricing_dashboard(request):
    """Display dynamic pricing dashboard for mall admin"""
    mall_id = request.session.get('mall_id')
    if not mall_id:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    today = timezone.now().date()
    
    context = {
        'uname': request.session.get('uname', 'User'),
        'mall_id': mall_id,
        'today': today.isoformat(),
    }
    
    return render(request, 'admin/pricing_dashboard.html', context)


@csrf_exempt
@login_required
def api_dynamic_rates(request):
    """
    Get dynamic rates for a specific date and vehicle type
    """
    mall_id = request.session.get('mall_id')
    if not mall_id:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        date_str = request.GET.get('date', timezone.now().date().isoformat())
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        vehicle_type = request.GET.get('vehicle_type', None)
        
        query = DynamicRate.objects.filter(
            mall_id=mall_id,
            applicable_date=target_date,
            is_active=True
        )
        
        if vehicle_type:
            query = query.filter(vehicle_type=vehicle_type)
        
        rates = query.order_by('start_hour')
        
        data = {
            'date': target_date.isoformat(),
            'mall_id': mall_id,
            'rates': [
                {
                    'start_hour': r.start_hour,
                    'end_hour': r.end_hour,
                    'time_range': f'{r.start_hour:02d}:00-{r.end_hour:02d}:00',
                    'vehicle_type': r.vehicle_type,
                    'base_rate': float(r.base_rate_per_hour),
                    'dynamic_rate': float(r.dynamic_rate_per_hour),
                    'multiplier': r.price_multiplier,
                    'change_percentage': round((r.price_multiplier - 1.0) * 100, 1),
                    'demand_level': r.demand_level,
                    'occupancy_rate': r.occupancy_rate,
                    'reason': r.reason,
                }
                for r in rates
            ]
        }
        
        return JsonResponse(data)
        
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    except Exception as e:
        logger.error(f"Error fetching dynamic rates: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@login_required
def api_discount_hours(request):
    """
    Get hours with discounted pricing
    Useful for marketing/promotion
    """
    mall_id = request.session.get('mall_id')
    if not mall_id:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        vehicle_type = request.GET.get('vehicle_type', 'Car')
        days_ahead = int(request.GET.get('days_ahead', 7))
        
        data = {
            'discount_opportunities': []
        }
        
        for day_offset in range(days_ahead):
            date = (timezone.now() + timedelta(days=day_offset)).date()
            
            rates = DynamicRate.objects.filter(
                mall_id=mall_id,
                vehicle_type=vehicle_type,
                applicable_date=date,
                is_active=True,
                price_multiplier__lt=1.0
            ).order_by('start_hour')
            
            for rate in rates:
                discount_pct = abs(rate.get_discount_percentage())
                data['discount_opportunities'].append({
                    'date': date.isoformat(),
                    'time_range': f'{rate.start_hour:02d}:00-{rate.end_hour:02d}:00',
                    'discount_percentage': round(discount_pct, 1),
                    'dynamic_rate': float(rate.dynamic_rate_per_hour),
                    'occupancy_rate': rate.occupancy_rate,
                })
        
        return JsonResponse(data)
        
    except Exception as e:
        logger.error(f"Error fetching discount hours: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@login_required
def api_surge_pricing(request):
    """
    Get hours with surge pricing (price increases)
    """
    mall_id = request.session.get('mall_id')
    if not mall_id:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        vehicle_type = request.GET.get('vehicle_type', 'Car')
        days_ahead = int(request.GET.get('days_ahead', 7))
        
        data = {
            'surge_pricing': []
        }
        
        for day_offset in range(days_ahead):
            date = (timezone.now() + timedelta(days=day_offset)).date()
            
            rates = DynamicRate.objects.filter(
                mall_id=mall_id,
                vehicle_type=vehicle_type,
                applicable_date=date,
                is_active=True,
                price_multiplier__gt=1.0
            ).order_by('start_hour')
            
            for rate in rates:
                surge_pct = rate.get_discount_percentage()
                data['surge_pricing'].append({
                    'date': date.isoformat(),
                    'time_range': f'{rate.start_hour:02d}:00-{rate.end_hour:02d}:00',
                    'surge_percentage': round(surge_pct, 1),
                    'dynamic_rate': float(rate.dynamic_rate_per_hour),
                    'demand_level': rate.demand_level,
                    'occupancy_rate': rate.occupancy_rate,
                })
        
        return JsonResponse(data)
        
    except Exception as e:
        logger.error(f"Error fetching surge pricing: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@login_required
def api_revenue_impact(request):
    """
    Get estimated revenue impact of dynamic pricing
    """
    mall_id = request.session.get('mall_id')
    if not mall_id:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        date_str = request.GET.get('date', timezone.now().date().isoformat())
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        dynamic_rates = DynamicRate.objects.filter(
            mall_id=mall_id,
            applicable_date=target_date
        )
        
        total_base = sum(float(r.base_rate_per_hour) * (r.end_hour - r.start_hour) for r in dynamic_rates)
        total_dynamic = sum(float(r.dynamic_rate_per_hour) * (r.end_hour - r.start_hour) for r in dynamic_rates)
        
        impact = total_dynamic - total_base
        impact_pct = (impact / total_base * 100) if total_base > 0 else 0
        
        data = {
            'date': target_date.isoformat(),
            'estimated_base_revenue': round(total_base, 2),
            'estimated_dynamic_revenue': round(total_dynamic, 2),
            'estimated_revenue_increase': round(impact, 2),
            'increase_percentage': round(impact_pct, 2),
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        logger.error(f"Error calculating revenue impact: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
