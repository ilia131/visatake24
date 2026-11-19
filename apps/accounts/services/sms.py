import logging
import re

import requests
from django.conf import settings


logger = logging.getLogger(__name__)


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

    if template_id <= 0:
        raise SMSIRError("Invalid SMS.ir template ID.")

    if not re.fullmatch(r"\+989[0-9]{9}", phone_number):
        raise SMSIRError("SMS.ir requires an Iranian mobile number.")

    url = "https://api.sms.ir/v1/send/verify"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-API-KEY": api_key,
    }

    payload = {
        "mobile": "0" + phone_number[3:],
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
            allow_redirects=False,
        )

        response.raise_for_status()
        result = response.json()

    except requests.RequestException as exc:
        http_status = exc.response.status_code if exc.response is not None else None
        logger.warning("SMS.ir request failed (HTTP %s).", http_status)
        raise SMSIRError("SMS.ir connection or sending failed.") from None

    except ValueError:
        raise SMSIRError("Invalid SMS.ir response.") from None

    provider_status = result.get("status") if isinstance(result, dict) else None
    if not 200 <= response.status_code < 300 or provider_status != 1:
        logger.warning(
            "SMS.ir rejected request (HTTP %s, status %s).",
            response.status_code,
            provider_status if type(provider_status) is int else None,
        )
        raise SMSIRError("SMS.ir rejected the request.")

    data = result.get("data")
    message_id = data.get("messageId") if isinstance(data, dict) else None
    logger.info(
        "SMS.ir accepted request (HTTP %s, status %s, message ID %s).",
        response.status_code,
        provider_status,
        message_id if type(message_id) is int else None,
    )
