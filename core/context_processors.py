from django.conf import settings

def sms_credentials(request):
    """
    Exposes a boolean flag representing whether SMS gateway API keys are defined.
    """
    return {
        'SMS_GATEWAY_API_KEY_DEFINED': bool(getattr(settings, 'SMS_GATEWAY_API_KEY', '')),
    }
