from django.utils import timezone
from django.utils.dateparse import parse_date
from datetime import date


class TemporalFilterService:
    @staticmethod
    def parse_filters(request):
        filters = {}
        
        if start_date := request.GET.get('start_date'):
            if parsed_start := parse_date(start_date):
                filters['start_date'] = parsed_start
        
        if end_date := request.GET.get('end_date'):
            if parsed_end := parse_date(end_date):
                filters['end_date'] = parsed_end
        
        for param in ['year', 'month']:
            if value := request.GET.get(param):
                try:
                    filters[param] = int(value)
                except (ValueError, TypeError):
                    pass
        
        return filters
    
    @staticmethod
    def get_context(year=None, month=None):
        now = timezone.now()
        current_year = year or now.year
        current_month = month or now.month
        
        month_names = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        
        current_month_name = month_names[current_month - 1] if current_month else None
        
        available_years = list(range(2025, now.year + 2))
        available_months = [(i, month_names[i - 1]) for i in range(1, 13)]
        
        return {
            'current_year': current_year,
            'current_month': current_month,
            'current_month_name': current_month_name,
            'available_years': available_years,
            'available_months': available_months,
        }


class TemporalDataService:
    @staticmethod
    def get_available_years():
        current_year = timezone.now().year
        return list(range(2025, current_year + 2))
    
    @staticmethod
    def get_current_year():
        return timezone.now().year
    
    @staticmethod
    def get_current_month():
        return timezone.now().month
    
    @staticmethod
    def get_year_month_choices():
        current_date = timezone.now()
        current_year = current_date.year
        current_month = current_date.month
        
        choices = []
        for year in range(2025, current_year + 2):
            for month in range(1, 13):
                if year == current_year and month > current_month:
                    break
                month_name = date(year, month, 1).strftime('%B %Y')
                choices.append((f"{year}-{month:02d}", month_name))
        
        return choices


def parse_temporal_filters(request):
    return TemporalFilterService.parse_filters(request)


def get_temporal_context(year=None, month=None):
    return TemporalFilterService.get_context(year, month)


def get_available_years():
    return TemporalDataService.get_available_years()
