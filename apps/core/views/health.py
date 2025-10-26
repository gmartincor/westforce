from django.http import JsonResponse
from django.db import connection
from django.conf import settings
import traceback


def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        ct_status = "unknown"
        try:
            from django.contrib.contenttypes.models import ContentType
            ct_count = ContentType.objects.count()
            ct_status = f"OK: {ct_count} content types"
        except Exception as e:
            ct_status = f"ERROR: {e}"
        
        auth_status = "unknown"
        try:
            from apps.authentication.models import User
            user_count = User.objects.count()
            auth_status = f"OK: {user_count} users"
        except Exception as e:
            auth_status = f"ERROR: {e}"
        
        return JsonResponse({
            "status": "healthy",
            "environment": getattr(settings, 'ENVIRONMENT', 'unknown'),
            "debug": settings.DEBUG,
            "database": "OK",
            "content_types": ct_status,
            "authentication": auth_status,
            "app_name": "Westforce"
        })
    
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc() if settings.DEBUG else None
        }, status=500)
