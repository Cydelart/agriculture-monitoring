"""
Simple management command to run Iris detection.

Usage:
    python manage.py detect_anomalies
    python manage.py detect_anomalies --plot 1
    python manage.py detect_anomalies --minutes 10
"""
from django.core.management.base import BaseCommand
from mlmodule.iris_service import run_batch_detection


class Command(BaseCommand):
    help = "Run Iris anomaly detection"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--plot',
            type=int,
            help='Specific plot ID to check'
        )
        parser.add_argument(
            '--minutes',
            type=int,
            default=5,
            help='Minutes of data to analyze (default: 5)'
        )
        parser.add_argument(
            '--no-save',
            action='store_true',
            help='Do not save events to database'
        )
    
    def handle(self, *args, **options):
        plot_id = options['plot']
        minutes = options['minutes']
        create_events = not options['no_save']
        
        # Run detection
        run_batch_detection(
            plot_id=plot_id,
            minutes=minutes,
            create_events=create_events
        )
