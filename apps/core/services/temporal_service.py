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
        current_year = now.year
        current_month = now.month
        
        return {
            'current_year': current_year,
            'current_month': current_month,
            'selected_year': year or current_year,
            'selected_month': month or current_month,
            'years': list(range(current_year - 5, current_year + 1)),
            'months': [
                {'value': i, 'name': date(2000, i, 1).strftime('%B')}
                for i in range(1, 13)
            ]
        }


class TemporalDataService:
    @staticmethod
    def get_available_years():
        current_year = timezone.now().year
        return list(range(2020, current_year + 2))
    
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
        for year in range(2020, current_year + 2):
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
