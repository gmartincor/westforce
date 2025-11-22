import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from apps.core.services.email_service import get_email_service

logger = logging.getLogger(__name__)


@require_http_methods(["POST"])
def quote_request(request):
    try:
        data = json.loads(request.body)
        logger.info(f"Quote request received: {data.get('firstName')} {data.get('lastName')}")
        
        required_fields = ['bedrooms', 'fromSuburb', 'toSuburb', 'moveDate', 'startTime', 
                          'firstName', 'lastName', 'mobile', 'email']
        
        for field in required_fields:
            if not data.get(field):
                logger.warning(f"Missing required field: {field}")
                return JsonResponse({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }, status=400)
        
        try:
            email_service = get_email_service()
            result = email_service.send_quote_notification(data)
            logger.info(f"Quote email sent successfully: {result}")
        except Exception as e:
            logger.error(f"Failed to send quote email: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': 'Failed to send email notification'
            }, status=500)
        
        return JsonResponse({
            'success': True,
            'message': 'Quote request received successfully'
        })
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Invalid request data'
        }, status=400)
    except Exception as e:
        logger.error(f"Quote request error: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'An error occurred processing your request'
        }, status=500)
