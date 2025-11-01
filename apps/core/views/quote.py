import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone


@require_http_methods(["POST"])
def quote_request(request):
    try:
        data = json.loads(request.body)
        
        bedrooms = data.get('bedrooms', '')
        from_suburb = data.get('fromSuburb', '')
        to_suburb = data.get('toSuburb', '')
        move_date = data.get('moveDate', '')
        flexible_dates = data.get('flexibleDates', False)
        start_time = data.get('startTime', '')
        additional_stop = data.get('additionalStop', False)
        large_items = data.get('largeItems', False)
        packing_service = data.get('packingService', 'not-required')
        storage = data.get('storage', False)
        first_name = data.get('firstName', '')
        last_name = data.get('lastName', '')
        mobile = data.get('mobile', '')
        email = data.get('email', '')
        comments = data.get('comments', '')
        hear_about = data.get('hearAbout', '')
        newsletter = data.get('newsletter', False)
        
        email_subject = f'New Quote Request - {first_name} {last_name}'
        email_body = f"""
New Quote Request Received

CONTACT DETAILS:
Name: {first_name} {last_name}
Mobile: {mobile}
Email: {email}

MOVE DETAILS:
Property Size: {bedrooms} bedroom(s)
From: {from_suburb}
To: {to_suburb}
Move Date: {move_date}
Flexible Dates: {'Yes' if flexible_dates else 'No'}
Preferred Start Time: {start_time}
Additional Stop: {'Yes' if additional_stop else 'No'}

SERVICES:
Large/Heavy Items: {'Yes' if large_items else 'No'}
Packing Service: {packing_service}
Storage Required: {'Yes' if storage else 'No'}

ADDITIONAL INFO:
How they heard about us: {hear_about}
Newsletter Subscription: {'Yes' if newsletter else 'No'}
Comments: {comments if comments else 'None'}

---
Submitted: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        try:
            send_mail(
                email_subject,
                email_body,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
        except Exception as e:
            pass
        
        return JsonResponse({
            'success': True,
            'message': 'Quote request received successfully'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid request data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'An error occurred processing your request'
        }, status=500)
