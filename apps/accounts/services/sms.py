
import requests
from django.conf import settings


class SMSIRError(Exception):
    pass


def send_sms_otp(phone_number: str, code: str) -> None:
    api_key = settings.SMSIR_API_KEY
    template_id = settings.SMSIR_OTP_TEMPLATE_ID

    if not api_key or not template_id:
        raise SMSIRError("SMS.ir configuration is missing.")

    try:
        template_id = int(template_id)
    except (TypeError, ValueError) as exc:
        raise SMSIRError("Invalid SMS.ir template ID.") from exc

    url = "https://api.sms.ir/v1/send/verify"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-API-KEY": api_key,
    }

    payload = {
        "mobile": phone_number,
        "templateId": template_id,
        "parameters": [
            {
                "name": "CODE",
                "value": str(code),
            }
        ],
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=15,
        )

        response.raise_for_status()
        result = response.json()

    except requests.RequestException as exc:
        raise SMSIRError("SMS.ir connection or sending failed.") from exc

    except ValueError as exc:
        raise SMSIRError("Invalid SMS.ir response.") from exc

    if result.get("status") != 1:
        raise SMSIRError(
            result.get("message", "SMS.ir rejected the request.")
        )
