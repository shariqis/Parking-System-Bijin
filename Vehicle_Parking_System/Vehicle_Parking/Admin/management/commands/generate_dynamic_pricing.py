"""
Management command to generate dynamic pricing
Run after occupancy forecasts are generated
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import timedelta
from Admin.dynamic_pricing import DynamicPricingEngine, run_all_malls_dynamic_pricing
from Admin.models import User
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generate dynamic pricing based on occupancy forecasts'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--mall-id',
            type=int,
            help='Specific mall ID for pricing. If not provided, prices all malls.'
        )
        parser.add_argument(
            '--days-ahead',
            type=int,
            default=7,
            help='Number of days ahead to generate pricing (default: 7)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually saving'
        )
        parser.add_argument(
            '--show-impact',
            action='store_true',
            help='Show estimated revenue impact'
        )
    
    def handle(self, *args, **options):
        mall_id = options.get('mall_id')
        days_ahead = options.get('days_ahead', 7)
        dry_run = options.get('dry_run', False)
        show_impact = options.get('show_impact', False)
        
        try:
            if mall_id:
                self._generate_pricing_single_mall(mall_id, days_ahead, dry_run, show_impact)
            else:
                self._generate_pricing_all_malls(days_ahead, dry_run, show_impact)
                
        except Exception as e:
            raise CommandError(f'Failed to generate dynamic pricing: {str(e)}')
    
    def _generate_pricing_single_mall(self, mall_id, days_ahead, dry_run, show_impact):
        """Generate dynamic pricing for a single mall"""
        try:
            mall = User.objects.get(id=mall_id, is_customer=2)
        except User.DoesNotExist:
            raise CommandError(f'Mall with ID {mall_id} not found')
        
        self.stdout.write(f'Generating dynamic pricing for {mall.username}...')
        
        engine = DynamicPricingEngine(mall_id)
        total_rates = 0
        
        for day_offset in range(days_ahead):
            target_date = (timezone.now() + timedelta(days=day_offset)).date()
            
            if dry_run:
                self.stdout.write(f'  [DRY RUN] Would generate rates for {target_date}')
                
                # Show sample rates
                sample_rates = engine.generate_dynamic_rates(target_date, ['Car'])
                if sample_rates:
                    self.stdout.write(f'    Sample: {len(sample_rates)} hourly rates for Car')
                    for rate in sample_rates[:3]:
                        change_pct = (rate.price_multiplier - 1.0) * 100
                        self.stdout.write(
                            f'      {rate.start_hour:02d}:00-{rate.end_hour:02d}:00: '
                            f'{rate.demand_level} ({rate.occupancy_rate:.1f}% occ) '
                            f'→ {change_pct:+.1f}% ({rate.dynamic_rate_per_hour:.2f})'
                        )
            else:
                count = engine.save_dynamic_rates(target_date)
                total_rates += count
                self.stdout.write(self.style.success(f'  ✓ Generated rates for {target_date}: {count} records'))
                
                if show_impact:
                    impact = engine.calculate_revenue_impact(target_date)
                    self.stdout.write(
                        f'    Revenue impact: ₹{impact["estimated_increase"]:.2f} '
                        f'({impact["increase_percentage"]:+.1f}%)'
                    )
        
        if not dry_run:
            self.stdout.write(
                self.style.success(f'Successfully created {total_rates} dynamic rates for {mall.username}')
            )
    
    def _generate_pricing_all_malls(self, days_ahead, dry_run, show_impact):
        """Generate dynamic pricing for all malls"""
        malls = User.objects.filter(is_customer=2, is_active=True)
        
        if not malls.exists():
            self.stdout.write(self.style.warning('No active malls found'))
            return
        
        self.stdout.write(f'Generating dynamic pricing for {malls.count()} malls ({days_ahead} days ahead)...')
        
        total_created = 0
        total_revenue_impact = 0
        
        for mall in malls:
            self.stdout.write(f'\n  Processing: {mall.username}')
            engine = DynamicPricingEngine(mall.id)
            
            for day_offset in range(days_ahead):
                target_date = (timezone.now() + timedelta(days=day_offset)).date()
                
                if dry_run:
                    self.stdout.write(f'    [DRY RUN] Would generate rates for {target_date}')
                else:
                    try:
                        count = engine.save_dynamic_rates(target_date)
                        total_created += count
                        self.stdout.write(f'    ✓ {target_date}: {count} records')
                        
                        if show_impact:
                            impact = engine.calculate_revenue_impact(target_date)
                            total_revenue_impact += impact['estimated_increase']
                            self.stdout.write(
                                f'      Revenue: ₹{impact["estimated_increase"]:.2f} '
                                f'({impact["increase_percentage"]:+.1f}%)'
                            )
                    except Exception as e:
                        self.stdout.write(self.style.error(f'    ✗ {target_date}: {str(e)}'))
        
        if not dry_run:
            msg = f'\n✓ Successfully created {total_created} dynamic rates'
            if show_impact:
                msg += f'\n  Estimated total revenue impact: ₹{total_revenue_impact:.2f}'
            self.stdout.write(self.style.success(msg))
        else:
            self.stdout.write(self.style.warning('\n[DRY RUN] No rates were actually created'))
