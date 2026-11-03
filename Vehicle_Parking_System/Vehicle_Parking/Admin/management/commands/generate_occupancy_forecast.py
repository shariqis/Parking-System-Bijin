"""
Management command to generate occupancy forecasts
Run this daily to update demand predictions
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import timedelta
from Admin.ml_occupancy_forecast import OccupancyPredictor, run_all_malls_forecast
from Admin.models import User
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generate occupancy forecasts for parking slots'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--mall-id',
            type=int,
            help='Specific mall ID to forecast. If not provided, forecasts all malls.'
        )
        parser.add_argument(
            '--days-ahead',
            type=int,
            default=7,
            help='Number of days ahead to forecast (default: 7)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually saving'
        )
    
    def handle(self, *args, **options):
        mall_id = options.get('mall_id')
        days_ahead = options.get('days_ahead', 7)
        dry_run = options.get('dry_run', False)
        
        try:
            if mall_id:
                self._forecast_single_mall(mall_id, days_ahead, dry_run)
            else:
                self._forecast_all_malls(days_ahead, dry_run)
                
        except Exception as e:
            raise CommandError(f'Failed to generate forecasts: {str(e)}')
    
    def _forecast_single_mall(self, mall_id, days_ahead, dry_run):
        """Generate forecast for a single mall"""
        try:
            mall = User.objects.get(id=mall_id, is_customer=2)
        except User.DoesNotExist:
            raise CommandError(f'Mall with ID {mall_id} not found')
        
        self.stdout.write(f'Generating forecasts for {mall.username}...')
        
        predictor = OccupancyPredictor(mall_id)
        total_forecasts = 0
        
        for day_offset in range(1, days_ahead + 1):
            forecast_date = (timezone.now() + timedelta(days=day_offset)).date()
            
            if dry_run:
                self.stdout.write(f'  [DRY RUN] Would forecast {forecast_date}')
                # Show sample forecast
                sample_forecasts = predictor.forecast_demand(forecast_date, 'Car')
                self.stdout.write(f'    Sample: {len(sample_forecasts)} hourly forecasts per vehicle type')
            else:
                count = predictor.save_forecasts(forecast_date)
                total_forecasts += count
                self.stdout.write(self.style.success(f'  ✓ Forecasted {forecast_date}: {count} records'))
        
        if not dry_run:
            self.stdout.write(
                self.style.success(f'Successfully created {total_forecasts} forecasts for {mall.username}')
            )
    
    def _forecast_all_malls(self, days_ahead, dry_run):
        """Generate forecasts for all malls"""
        malls = User.objects.filter(is_customer=2, is_active=True)
        
        if not malls.exists():
            self.stdout.write(self.style.warning('No active malls found'))
            return
        
        self.stdout.write(f'Generating forecasts for {malls.count()} malls ({days_ahead} days ahead)...')
        
        total_created = 0
        
        for mall in malls:
            self.stdout.write(f'\n  Processing: {mall.username}')
            predictor = OccupancyPredictor(mall.id)
            
            for day_offset in range(1, days_ahead + 1):
                forecast_date = (timezone.now() + timedelta(days=day_offset)).date()
                
                if dry_run:
                    self.stdout.write(f'    [DRY RUN] Would forecast {forecast_date}')
                else:
                    try:
                        count = predictor.save_forecasts(forecast_date)
                        total_created += count
                        self.stdout.write(f'    ✓ {forecast_date}: {count} records')
                    except Exception as e:
                        self.stdout.write(self.style.error(f'    ✗ {forecast_date}: {str(e)}'))
        
        if not dry_run:
            self.stdout.write(
                self.style.success(f'\n✓ Successfully created {total_created} total forecasts')
            )
        else:
            self.stdout.write(self.style.warning('\n[DRY RUN] No forecasts were actually created'))
