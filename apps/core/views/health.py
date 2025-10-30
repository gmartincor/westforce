from django.http import JsonResponse
from django.db import connection
from django.conf import settings


def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        response_data = {
            "status": "healthy",
            "app": "Westforce",
            "database": "connected"
        }
        
        if settings.DEBUG:
            try:
                from django.contrib.contenttypes.models import ContentType
                ct_count = ContentType.objects.count()
                response_data["content_types"] = str(ct_count)
            except Exception as e:
                response_data["content_types_error"] = str(e)
            
            try:
                from apps.authentication.models import User
                user_count = User.objects.count()
                response_data["users"] = str(user_count)
            except Exception as e:
                response_data["users_error"] = str(e)
        
        return JsonResponse(response_data)
    
    except Exception as e:
        return JsonResponse({
            "status": "unhealthy",
            "error": "Database connection failed" if not settings.DEBUG else str(e)
        }, status=500)
