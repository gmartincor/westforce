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


def company_context(request):
    return {
        'company_name': getattr(settings, 'COMPANY_NAME', ''),
        'company_tagline': getattr(settings, 'COMPANY_TAGLINE', ''),
        'company_phone': getattr(settings, 'COMPANY_PHONE', ''),
        'company_phone_display': getattr(settings, 'COMPANY_PHONE_DISPLAY', ''),
        'company_email': getattr(settings, 'COMPANY_EMAIL', ''),
        'company_address_city': getattr(settings, 'COMPANY_ADDRESS_CITY', ''),
        'company_address_state': getattr(settings, 'COMPANY_ADDRESS_STATE', ''),
        'company_address_country': getattr(settings, 'COMPANY_ADDRESS_COUNTRY', ''),
        'company_latitude': getattr(settings, 'COMPANY_LATITUDE', ''),
        'company_longitude': getattr(settings, 'COMPANY_LONGITUDE', ''),
        'company_rating': getattr(settings, 'COMPANY_RATING', ''),
        'company_review_count': getattr(settings, 'COMPANY_REVIEW_COUNT', ''),
        'company_established_year': getattr(settings, 'COMPANY_ESTABLISHED_YEAR', ''),
    }


def seo_context(request):
    return {
        'seo_meta_title': getattr(settings, 'SEO_META_TITLE', ''),
        'seo_meta_description': getattr(settings, 'SEO_META_DESCRIPTION', ''),
        'seo_og_image_path': getattr(settings, 'SEO_OG_IMAGE_PATH', ''),
    }
