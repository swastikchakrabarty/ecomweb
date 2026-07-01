def generate_pdf_bytes(title, content):
    """
    Generates a valid PDF 1.4 document containing the text content.
    No third-party libraries needed.
    """
    lines = content.split('\n')
    pdf = bytearray()
    
    # PDF Header
    pdf.extend(b"%PDF-1.4\n")
    
    objects = []
    
    def add_object(obj_bytes):
        obj_id = len(objects) + 1
        objects.append((len(pdf), obj_id))
        pdf.extend(f"{obj_id} 0 obj\n".encode('ascii'))
        pdf.extend(obj_bytes)
        pdf.extend(b"\nendobj\n")
        return obj_id

    # Font definitions (Standard Helvetica)
    font_def = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"
    
    # We will build the page stream content
    stream_content = bytearray()
    stream_content.extend(b"BT\n/F1 10 Tf\n50 720 Td\n14 TL\n")
    
    # Add title
    escaped_title = title.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
    stream_content.extend(f"({escaped_title}) Tj T*\n".encode('utf-8'))
    stream_content.extend(b"T*\n")
    
    # Add each line
    for line in lines:
        escaped_line = line.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
        stream_content.extend(f"({escaped_line}) Tj T*\n".encode('utf-8'))
        
    stream_content.extend(b"ET\n")
    
    # Catalog
    add_object(b"<< /Type /Catalog /Pages 2 0 R >>")
    # Pages
    add_object(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    # Page
    add_object(b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>")
    # Content Stream
    content_stream_len = len(stream_content)
    content_obj_bytes = f"<< /Length {content_stream_len} >>\nstream\n".encode('ascii') + stream_content + b"\nendstream"
    add_object(content_obj_bytes)
    # Font
    add_object(font_def)
    
    # Xref table
    xref_pos = len(pdf)
    pdf.extend(b"xref\n")
    pdf.extend(f"0 {len(objects) + 1}\n".encode('ascii'))
    pdf.extend(b"0000000000 65535 f \n")
    for pos, obj_id in objects:
        pdf.extend(f"{pos:010d} 00000 n \n".encode('ascii'))
        
    pdf.extend(b"trailer\n")
    pdf.extend(f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n".encode('ascii'))
    pdf.extend(b"startxref\n")
    pdf.extend(f"{xref_pos}\n".encode('ascii'))
    pdf.extend(b"%%EOF\n")
    
    return bytes(pdf)


# ---------------------------------------------------------------------------
# Twilio Live SMS Helpers
# ---------------------------------------------------------------------------

import logging

logger = logging.getLogger(__name__)


def send_otp_sms(phone_number: str, otp_code: str) -> bool:
    """
    Dispatch a live OTP via Twilio REST API.

    Args:
        phone_number: 10-digit Indian mobile number (digits only, no country code).
        otp_code:     4-digit OTP string.

    Returns:
        True  – message queued successfully by Twilio.
        False – Twilio rejected the request or library is unavailable.
    """
    from django.conf import settings

    # Guard: skip live dispatch if Twilio credentials are absent
    if not (hasattr(settings, 'TWILIO_ACCOUNT_SID') and settings.TWILIO_ACCOUNT_SID):
        logger.warning("[Twilio OTP] Credentials not configured – simulating delivery.")
        return False

    # Normalise to E.164 (+91 for India)
    e164_number = f"+91{phone_number[-10:]}"

    try:
        from twilio.rest import Client
        from twilio.base.exceptions import TwilioRestException

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=(
                f"Your KaaNuRO Group verification code is {otp_code}. "
                f"Valid for 5 minutes. Do not share this code with anyone."
            ),
            from_=settings.TWILIO_NUMBER,
            to=e164_number,
        )
        logger.info("[Twilio OTP] SID=%s  to=%s  status=%s", message.sid, e164_number, message.status)
        return True

    except ImportError:
        logger.error("[Twilio OTP] 'twilio' package is not installed – falling back to simulation.")
        return False

    except Exception as exc:  # covers TwilioRestException and any network errors
        logger.error("[Twilio OTP] Error: %s  (phone=%s)", exc, e164_number)
        return False


def send_order_confirmation_sms(phone_number: str, customer_name: str, order_id: str) -> bool:
    """
    Send an order-confirmation alert with an invoice deep-link via Twilio.

    Args:
        phone_number:  10-digit Indian mobile number (digits only, no country code).
        customer_name: Display name of the customer.
        order_id:      Primary-key / UUID of the Order record.

    Returns:
        True  – message queued by Twilio.
        False – Twilio rejected the call or library is unavailable.
    """
    from django.conf import settings

    # Guard: skip live dispatch if Twilio credentials are absent
    if not (hasattr(settings, 'TWILIO_ACCOUNT_SID') and settings.TWILIO_ACCOUNT_SID):
        logger.warning("[Twilio Order] Credentials not configured – skipping SMS.")
        return False

    e164_number = f"+91{phone_number[-10:]}"
    invoice_url = f"http://127.0.0.1:8082/orders/{order_id}/invoice/"

    body = (
        f"Hello {customer_name}, your KaaNuRO Group order has been confirmed "
        f"successfully! View your print-ready invoice statement here: {invoice_url}"
    )

    try:
        from twilio.rest import Client
        from twilio.base.exceptions import TwilioRestException

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=body,
            from_=settings.TWILIO_NUMBER,
            to=e164_number,
        )
        logger.info(
            "[Twilio Order] SID=%s  to=%s  status=%s  order=%s",
            message.sid, e164_number, message.status, order_id,
        )
        return True

    except ImportError:
        logger.error("[Twilio Order] 'twilio' package is not installed – skipping SMS dispatch.")
        return False

    except Exception as exc:  # covers TwilioRestException and any network errors
        logger.error("[Twilio Order] Error: %s  (phone=%s  order=%s)", exc, e164_number, order_id)
        return False

