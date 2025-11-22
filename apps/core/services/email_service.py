from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import resend
from django.conf import settings


class EmailProvider(ABC):
    @abstractmethod
    def send(self, to: str, subject: str, body: str, html: Optional[str] = None) -> Dict[str, Any]:
        pass


class ResendEmailProvider(EmailProvider):
    def __init__(self, api_key: str):
        resend.api_key = api_key
        self.from_email = getattr(settings, 'RESEND_FROM_EMAIL', 'onboarding@resend.dev')

    def send(self, to: str, subject: str, body: str, html: Optional[str] = None) -> Dict[str, Any]:
        params = {
            "from": self.from_email,
            "to": [to],
            "subject": subject,
        }
        
        if html:
            params["html"] = html
        else:
            params["text"] = body
            
        return resend.Emails.send(params)


class EmailService:
    def __init__(self, provider: EmailProvider):
        self._provider = provider

    def send_quote_notification(self, quote_data: Dict[str, Any]) -> Dict[str, Any]:
        to = getattr(settings, 'QUOTE_RECIPIENT_EMAIL', settings.COMPANY_EMAIL)
        subject = f"New Quote Request - {quote_data['firstName']} {quote_data['lastName']}"
        
        html_body = self._build_quote_html(quote_data)
        text_body = self._build_quote_text(quote_data)
        
        return self._provider.send(to=to, subject=subject, body=text_body, html=html_body)

    def _build_quote_text(self, data: Dict[str, Any]) -> str:
        return f"""
New Quote Request Received

CONTACT DETAILS:
Name: {data['firstName']} {data['lastName']}
Mobile: {data['mobile']}
Email: {data['email']}

MOVE DETAILS:
Property Size: {data['bedrooms']} bedroom(s)
From: {data['fromSuburb']}
To: {data['toSuburb']}
Move Date: {data['moveDate']}
Flexible Dates: {'Yes' if data.get('flexibleDates') else 'No'}
Preferred Start Time: {data['startTime']}
Additional Stop: {'Yes' if data.get('additionalStop') else 'No'}

SERVICES:
Large/Heavy Items: {'Yes' if data.get('largeItems') else 'No'}
Packing Service: {data['packingService']}
Storage Required: {'Yes' if data.get('storage') else 'No'}

ADDITIONAL INFO:
How they heard about us: {data.get('hearAbout', 'Not specified')}
Newsletter Subscription: {'Yes' if data.get('newsletter') else 'No'}
Comments: {data.get('comments') or 'None'}
        """

    def _build_quote_html(self, data: Dict[str, Any]) -> str:
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #1e3a8a; color: white; padding: 20px; text-align: center; }}
        .section {{ margin: 20px 0; padding: 15px; background-color: #f9fafb; border-radius: 8px; }}
        .section-title {{ font-weight: bold; color: #1e3a8a; margin-bottom: 10px; font-size: 16px; }}
        .info-row {{ margin: 8px 0; }}
        .label {{ font-weight: 600; color: #374151; }}
        .value {{ color: #1f2937; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 2px solid #e5e7eb; text-align: center; color: #6b7280; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>New Quote Request</h1>
        </div>
        
        <div class="section">
            <div class="section-title">Contact Details</div>
            <div class="info-row"><span class="label">Name:</span> <span class="value">{data['firstName']} {data['lastName']}</span></div>
            <div class="info-row"><span class="label">Mobile:</span> <span class="value">{data['mobile']}</span></div>
            <div class="info-row"><span class="label">Email:</span> <span class="value">{data['email']}</span></div>
        </div>
        
        <div class="section">
            <div class="section-title">Move Details</div>
            <div class="info-row"><span class="label">Property Size:</span> <span class="value">{data['bedrooms']} bedroom(s)</span></div>
            <div class="info-row"><span class="label">From:</span> <span class="value">{data['fromSuburb']}</span></div>
            <div class="info-row"><span class="label">To:</span> <span class="value">{data['toSuburb']}</span></div>
            <div class="info-row"><span class="label">Move Date:</span> <span class="value">{data['moveDate']}</span></div>
            <div class="info-row"><span class="label">Flexible Dates:</span> <span class="value">{'Yes' if data.get('flexibleDates') else 'No'}</span></div>
            <div class="info-row"><span class="label">Preferred Start Time:</span> <span class="value">{data['startTime']}</span></div>
            <div class="info-row"><span class="label">Additional Stop:</span> <span class="value">{'Yes' if data.get('additionalStop') else 'No'}</span></div>
        </div>
        
        <div class="section">
            <div class="section-title">Services Required</div>
            <div class="info-row"><span class="label">Large/Heavy Items:</span> <span class="value">{'Yes' if data.get('largeItems') else 'No'}</span></div>
            <div class="info-row"><span class="label">Packing Service:</span> <span class="value">{data['packingService']}</span></div>
            <div class="info-row"><span class="label">Storage Required:</span> <span class="value">{'Yes' if data.get('storage') else 'No'}</span></div>
        </div>
        
        <div class="section">
            <div class="section-title">Additional Information</div>
            <div class="info-row"><span class="label">How they heard about us:</span> <span class="value">{data.get('hearAbout', 'Not specified')}</span></div>
            <div class="info-row"><span class="label">Newsletter Subscription:</span> <span class="value">{'Yes' if data.get('newsletter') else 'No'}</span></div>
            <div class="info-row"><span class="label">Comments:</span> <span class="value">{data.get('comments') or 'None'}</span></div>
        </div>
        
        <div class="footer">
            <p>This quote request was submitted through the WestForce Removals website.</p>
        </div>
    </div>
</body>
</html>
        """


def get_email_service() -> EmailService:
    api_key = getattr(settings, 'RESEND_API_KEY', '')
    if not api_key:
        raise ValueError("RESEND_API_KEY not configured in settings")
    
    provider = ResendEmailProvider(api_key)
    return EmailService(provider)
