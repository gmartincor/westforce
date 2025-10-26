from django.core.management.base import BaseCommand
from django.core.management import execute_from_command_line
import os
import sys


class Command(BaseCommand):
    help = 'Start development server in different modes'

    def add_arguments(self, parser):
        parser.add_argument(
            'mode',
            choices=['manager', 'landing'],
            help='Server mode: manager (default) or landing'
        )
        parser.add_argument(
            '--port',
            type=int,
            default=8000,
            help='Port to run server on'
        )

    def handle(self, *args, **options):
        mode = options['mode']
        port = options['port']
        
        if mode == 'landing':
            os.environ['DEV_FORCE_LANDING'] = 'True'
            self.stdout.write(
                self.style.SUCCESS(f'Starting LANDING PAGE server on port {port}')
            )
            self.stdout.write('Access at: http://localhost:{}/'.format(port))
        else:
            os.environ['DEV_FORCE_LANDING'] = 'False'
            self.stdout.write(
                self.style.SUCCESS(f'Starting MANAGER PANEL server on port {port}')
            )
            self.stdout.write('Access at: http://localhost:{}/'.format(port))
            self.stdout.write('Login: westforce / westforce')
        
        execute_from_command_line(['manage.py', 'runserver', f'0.0.0.0:{port}'])
