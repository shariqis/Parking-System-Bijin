# Phase 2 Implementation Guide: Occupancy Forecasting & Dynamic Pricing

## Overview

Phase 2 implements two core AI features:
1. **Occupancy Forecasting** - Predicts parking demand based on historical booking patterns
2. **Dynamic Pricing** - Adjusts rates automatically based on predicted occupancy

## 📦 Installation & Setup

### 1. Install New Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `scikit-learn==1.3.2` - Machine learning models
- `pandas==2.1.3` - Data analysis
- `scipy==1.11.4` - Scientific computing
- `statsmodels==0.14.0` - Time-series analysis
- `joblib==1.3.2` - Model serialization

### 2. Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

This creates new tables for:
- `OccupancyForecast` - Stores occupancy predictions
- `DynamicRate` - Stores AI-calculated rates
- `AIMetrics` - Stores model performance metrics

---

## 🔧 Database Models

### OccupancyForecast
Stores predicted occupancy data for future time periods.

```
Fields:
- mall (FK)
- vehicle_type (Car/Bike)
- forecast_date (Date)
- hour (0-23)
- predicted_occupancy_rate (0-1)
- predicted_available_slots (Count)
- predicted_booked_slots (Count)
- confidence_score (0-1)
- demand_level (Low/Medium/High/Peak)
```

### DynamicRate
Stores calculated pricing tiers based on demand.

```
Fields:
- mall (FK)
- vehicle_type (Car/Bike)
- applicable_date (Date)
- start_hour / end_hour (Time range)
- base_rate_per_hour (Original rate)
- dynamic_rate_per_hour (AI-calculated rate)
- price_multiplier (1.2 = 20% increase)
- demand_level (Low/Medium/High/Peak)
- occupancy_rate (%)
- reason (Human-readable explanation)
```

### AIMetrics
Tracks performance of AI models.

```
Fields:
- mall (FK)
- forecast_mape (Mean Absolute Percentage Error)
- forecast_rmse (Root Mean Squared Error)
- forecast_accuracy (%)
- revenue_increase_percentage
- occupancy_change_percentage
- data_points_used
- last_training_date
```

---

## 🚀 Usage

### Occupancy Forecasting

#### A. Generate Forecasts via Management Command

```bash
# Forecast for all malls, 7 days ahead (default)
python manage.py generate_occupancy_forecast

# Forecast for specific mall
python manage.py generate_occupancy_forecast --mall-id 2

# Forecast 14 days ahead
python manage.py generate_occupancy_forecast --days-ahead 14

# Dry-run to preview without saving
python manage.py generate_occupancy_forecast --dry-run
```

#### B. Use OccupancyPredictor Programmatically

```python
from Admin.ml_occupancy_forecast import OccupancyPredictor
from datetime import datetime, timedelta

# Initialize predictor for a mall
predictor = OccupancyPredictor(mall_id=2, days_lookback=30)

# Get historical patterns
patterns = predictor.get_historical_data(vehicle_type='Car')
# Returns: {0: 0.15, 1: 0.12, ..., 23: 0.45}  # Hourly occupancy rates

# Generate forecast for a specific date
forecast_date = datetime.now().date()
forecasts = predictor.forecast_demand(forecast_date, 'Car')
# Returns: List of OccupancyForecast objects

# Save forecasts to database
count = predictor.save_forecasts(forecast_date)

# Get peak hours for the day
peak_hours = predictor.get_peak_hours(forecast_date, 'Car')
# Returns: [16, 17, 18, 19, 20]  # Peak hours

# Get low occupancy hours (for discounts)
low_hours = predictor.get_low_occupancy_hours(forecast_date, 'Car')
# Returns: [1, 2, 3, 4]  # Early morning hours
```

---

### Dynamic Pricing

#### A. Generate Dynamic Prices via Management Command

```bash
# Generate pricing for all malls, 7 days ahead
python manage.py generate_dynamic_pricing

# Generate for specific mall
python manage.py generate_dynamic_pricing --mall-id 2

# Show estimated revenue impact
python manage.py generate_dynamic_pricing --show-impact

# Dry-run preview
python manage.py generate_dynamic_pricing --dry-run
```

#### B. Use DynamicPricingEngine Programmatically

```python
from Admin.dynamic_pricing import DynamicPricingEngine
from datetime import datetime

# Initialize pricing engine
engine = DynamicPricingEngine(mall_id=2)

# Get current active rate
current_rate = engine.get_active_rate(vehicle_type='Car')
# Returns: DynamicRate object with current price

# Get rates for a specific date
target_date = datetime.now().date()
rates = engine.get_forecast_rates('Car', target_date)
# Returns: QuerySet of DynamicRate objects

# Get discount hours (for marketing)
discounts = engine.get_discount_hours('Car', target_date)
# Returns: [
#   {
#     'start_hour': 2,
#     'end_hour': 6,
#     'discount_percentage': 20.0,
#     'dynamic_rate': 40.0
#   },
#   ...
# ]

# Get surge pricing hours
surge = engine.get_peak_rate_hours('Car', target_date)
# Returns: [
#   {
#     'start_hour': 17,
#     'end_hour': 20,
#     'surge_percentage': 25.0,
#     'dynamic_rate': 62.5
#   },
#   ...
# ]

# Calculate revenue impact
impact = engine.calculate_revenue_impact(target_date)
# Returns: {
#   'estimated_base_revenue': 2400.0,
#   'estimated_dynamic_revenue': 2640.0,
#   'estimated_increase': 240.0,
#   'increase_percentage': 10.0
# }
```

---

## 📊 API Endpoints

All endpoints require login and mall authorization.

### Occupancy Forecasting APIs

#### 1. Get Occupancy Forecast
```
GET /adminApp/api/occupancy-forecast/
Query Parameters:
  - date (YYYY-MM-DD, optional, default: today)
  - vehicle_type (Car/Bike, optional, default: all)

Response:
{
  "date": "2024-05-15",
  "mall_id": 2,
  "forecasts": [
    {
      "hour": 10,
      "hour_display": "10:00",
      "vehicle_type": "Car",
      "occupancy_rate": 0.65,
      "occupancy_percentage": 65.0,
      "available_slots": 7,
      "booked_slots": 13,
      "confidence": 0.87,
      "demand_level": "High"
    },
    ...
  ]
}
```

#### 2. Get Peak Hours
```
GET /adminApp/api/peak-hours/
Query Parameters:
  - vehicle_type (default: Car)
  - days_ahead (default: 7)

Response:
{
  "peak_hours_by_day": [
    {
      "date": "2024-05-15",
      "peak_hours": [16, 17, 18, 19, 20],
      "peak_count": 5
    },
    ...
  ]
}
```

#### 3. Get Demand Prediction
```
GET /adminApp/api/demand-prediction/
Query Parameters:
  - days_ahead (default: 7)
  - vehicle_type (optional)

Response:
{
  "summary_by_date": [
    {
      "date": "2024-05-15",
      "day_name": "Wednesday",
      "average_occupancy": 0.62,
      "average_occupancy_pct": 62.0,
      "peak_demand_level": "High",
      "forecast_count": 48
    },
    ...
  ]
}
```

### Dynamic Pricing APIs

#### 4. Get Dynamic Rates
```
GET /adminApp/api/dynamic-rates/
Query Parameters:
  - date (YYYY-MM-DD, optional, default: today)
  - vehicle_type (optional)

Response:
{
  "date": "2024-05-15",
  "mall_id": 2,
  "rates": [
    {
      "start_hour": 10,
      "end_hour": 12,
      "time_range": "10:00-12:00",
      "vehicle_type": "Car",
      "base_rate": 50.0,
      "dynamic_rate": 57.5,
      "multiplier": 1.15,
      "change_percentage": 15.0,
      "demand_level": "High",
      "occupancy_rate": 75.0,
      "reason": "High demand (75.0% occupancy) - Price increased by 15.0%"
    },
    ...
  ]
}
```

#### 5. Get Discount Hours
```
GET /adminApp/api/discount-hours/
Query Parameters:
  - vehicle_type (default: Car)
  - days_ahead (default: 7)

Response:
{
  "discount_opportunities": [
    {
      "date": "2024-05-15",
      "time_range": "02:00-06:00",
      "discount_percentage": 20.0,
      "dynamic_rate": 40.0,
      "occupancy_rate": 25.0
    },
    ...
  ]
}
```

#### 6. Get Surge Pricing
```
GET /adminApp/api/surge-pricing/
Query Parameters:
  - vehicle_type (default: Car)
  - days_ahead (default: 7)

Response:
{
  "surge_pricing": [
    {
      "date": "2024-05-15",
      "time_range": "17:00-20:00",
      "surge_percentage": 25.0,
      "dynamic_rate": 62.5,
      "demand_level": "Peak",
      "occupancy_rate": 92.0
    },
    ...
  ]
}
```

#### 7. Get Revenue Impact
```
GET /adminApp/api/revenue-impact/
Query Parameters:
  - date (YYYY-MM-DD, optional, default: today)

Response:
{
  "date": "2024-05-15",
  "estimated_base_revenue": 2400.0,
  "estimated_dynamic_revenue": 2640.0,
  "estimated_revenue_increase": 240.0,
  "increase_percentage": 10.0
}
```

---

## 🎯 Pricing Strategy

### Multiplier Rules

| Occupancy | Demand | Multiplier | Change |
|-----------|--------|-----------|--------|
| 0-30% | Low | 0.80 | -20% (Discount) |
| 30-60% | Medium | 1.00 | 0% (Base) |
| 60-85% | High | 1.15 | +15% |
| 85-100% | Peak | 1.25 | +25% |

### Revenue Optimization

- **Low occupancy** → Offer discounts to fill slots
- **Medium occupancy** → Maintain base rates
- **High occupancy** → Apply moderate premium
- **Peak occupancy** → Maximum price increase

---

## 📈 How It Works

### Step 1: Historical Analysis
```
Analyzes bookings from past 30 days
↓
Calculates hourly occupancy patterns
↓
Identifies day-of-week variations
```

### Step 2: Demand Prediction
```
Detects peak hours (usually 5-8pm)
↓
Identifies low hours (usually 2-6am)
↓
Assigns confidence scores to predictions
```

### Step 3: Dynamic Pricing
```
Groups hours by demand patterns
↓
Calculates multipliers
↓
Generates pricing tiers
↓
Saves to database
```

### Step 4: Revenue Optimization
```
Estimates revenue impact
↓
Monitors booking patterns
↓
Adjusts multipliers for better ROI
```

---

## 🔄 Automated Scheduling

### Using Celery (Recommended)

```python
# settings.py
CELERY_BEAT_SCHEDULE = {
    'generate-forecasts': {
        'task': 'Admin.tasks.generate_daily_forecasts',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
    'generate-pricing': {
        'task': 'Admin.tasks.generate_daily_pricing',
        'schedule': crontab(hour=1, minute=0),  # Daily at 1am (after forecasts)
    },
}
```

### Using Cron (Simple Alternative)

```bash
# /etc/crontab
0 0 * * * cd /path/to/project && python manage.py generate_occupancy_forecast
0 1 * * * cd /path/to/project && python manage.py generate_dynamic_pricing
```

---

## 📊 Monitoring Performance

### Check Forecast Accuracy

```python
from Admin.models import OccupancyForecast
from User.models import Booking
from datetime import datetime, timedelta

# Get actual bookings from yesterday
yesterday = datetime.now().date() - timedelta(days=1)
actual_bookings = Booking.objects.filter(
    start_time__date=yesterday,
    parking_slot__mall_id=2
).count()

# Get forecast for yesterday
forecasts = OccupancyForecast.objects.filter(
    mall_id=2,
    forecast_date=yesterday
)

predicted_total = sum(f.predicted_booked_slots for f in forecasts)

accuracy = (1 - abs(actual - predicted) / actual) * 100
print(f"Forecast Accuracy: {accuracy:.1f}%")
```

### View AI Metrics

```python
from Admin.models import AIMetrics

metrics = AIMetrics.objects.filter(mall_id=2).latest('last_training_date')
print(f"Accuracy: {metrics.forecast_accuracy}%")
print(f"Revenue Impact: {metrics.revenue_increase_percentage}%")
```

---

## 🛠️ Troubleshooting

### Issue: Low forecast accuracy

**Solutions:**
- Ensure 30+ days of historical data exists
- Check for data quality issues
- Increase `days_lookback` parameter
- Verify time zone settings

### Issue: Revenue not increasing

**Causes:**
- Demand patterns not clear in data
- Base rates not optimized
- Multipliers too aggressive
- Need more booking history

**Solution:**
```python
# Adjust multiplier strategy
engine = DynamicPricingEngine(mall_id)
engine.LOW_MULTIPLIER = 0.75  # 25% discount
engine.PEAK_MULTIPLIER = 1.30  # 30% increase
```

### Issue: Forecasts not generating

**Check:**
1. Management command is running: `python manage.py generate_occupancy_forecast`
2. Database migrations completed: `python manage.py migrate`
3. Booking data exists in database
4. Required libraries installed: `pip list | grep scikit-learn`

---

## 📝 Example Workflow

### Day 1: Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run migrations
python manage.py migrate

# 3. Generate forecasts (test)
python manage.py generate_occupancy_forecast --mall-id 2 --dry-run
```

### Day 2: Generate Predictions
```bash
# Generate forecasts for next 7 days
python manage.py generate_occupancy_forecast --mall-id 2 --days-ahead 7

# Verify via API
curl "http://localhost:8000/adminApp/api/occupancy-forecast/?date=2024-05-16&vehicle_type=Car"
```

### Day 3: Generate Dynamic Pricing
```bash
# Generate pricing for next 7 days
python manage.py generate_dynamic_pricing --mall-id 2 --days-ahead 7 --show-impact

# Check discount hours
curl "http://localhost:8000/adminApp/api/discount-hours/?vehicle_type=Car"

# View revenue impact
curl "http://localhost:8000/adminApp/api/revenue-impact/?date=2024-05-16"
```

### Day 4+: Monitor & Optimize
```bash
# View forecast accuracy
python manage.py shell
>>> from Admin.models import AIMetrics
>>> m = AIMetrics.objects.filter(mall_id=2).latest('last_training_date')
>>> print(f"Accuracy: {m.forecast_accuracy}%")
```

---

## 🎓 Advanced Customization

### Custom Multiplier Strategy

```python
class CustomDynamicPricingEngine(DynamicPricingEngine):
    def calculate_optimal_multiplier(self, occupancy_rate, booking_velocity=None):
        # More aggressive pricing
        if occupancy_rate > 0.9:
            return min(self.MAX_MULTIPLIER, 1.5)  # 50% increase
        return super().calculate_optimal_multiplier(occupancy_rate, booking_velocity)
```

### Enhance Predictions

```python
class AdvancedOccupancyPredictor(OccupancyPredictor):
    def forecast_demand(self, forecast_date, vehicle_type='Car'):
        # Add weather data, events, etc.
        # Call parent method
        forecasts = super().forecast_demand(forecast_date, vehicle_type)
        
        # Apply event multipliers
        if is_special_event_day(forecast_date):
            for f in forecasts:
                f.predicted_occupancy_rate *= 1.3  # 30% more busy
        
        return forecasts
```

---

## 📞 Support

For issues or questions:
1. Check logs: `tail -f /var/log/django.log`
2. Review AIMetrics: `AIMetrics.objects.latest()`
3. Test with dry-run: `--dry-run` flag
4. Verify database: `python manage.py dbshell`

---

**Phase 2 Implementation Complete! 🎉**

Next step: Phase 3 (Advanced) - Chatbot & Computer Vision Monitoring
