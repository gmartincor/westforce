from django.conf import settings


def analytics_context(request):
    return {
        'GOOGLE_ANALYTICS_ID': getattr(settings, 'GOOGLE_ANALYTICS_ID', ''),
        'GOOGLE_TAG_MANAGER_ID': getattr(settings, 'GOOGLE_TAG_MANAGER_ID', ''),
        'GOOGLE_ADS_ID': getattr(settings, 'GOOGLE_ADS_ID', ''),
        'GOOGLE_ADS_CONVERSION_ID': getattr(settings, 'GOOGLE_ADS_CONVERSION_ID', ''),
        'GOOGLE_ADS_PHONE_CONVERSION_LABEL': getattr(settings, 'GOOGLE_ADS_PHONE_CONVERSION_LABEL', ''),
        'GOOGLE_ADS_EMAIL_CONVERSION_LABEL': getattr(settings, 'GOOGLE_ADS_EMAIL_CONVERSION_LABEL', ''),
        'GOOGLE_ADS_QUOTE_CONVERSION_LABEL': getattr(settings, 'GOOGLE_ADS_QUOTE_CONVERSION_LABEL', ''),
    }
