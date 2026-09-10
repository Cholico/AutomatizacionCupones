import json
import random
from urllib.parse import quote

from requests.exceptions import ConnectionError, Timeout
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from src.config import settings
from src.core.respuestas_twilio import RESPUESTAS_OK
from src.schemas.schemas import RespuestaTwilio


def enviar_mensaje_por_whatsapp(
    link_img: str, telefono: str, empleado, fecha_vencimiento, producto: str
) -> RespuestaTwilio:

    client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
    clave = random.choice(list(RESPUESTAS_OK.keys()))

    link_limpio = quote(link_img, safe=":/._-")

    try:
        message = client.messages.create(
            from_="whatsapp:+19789843312",
            content_sid=settings.TEMPLATE_SID,
            content_variables=json.dumps(
                {
                    "1": empleado,
                    "2": producto,
                    "3": fecha_vencimiento,
                    "4": RESPUESTAS_OK[clave],
                    "5": link_limpio,
                }
            ),
            to=f"whatsapp:+521{telefono}",
        )

        return RespuestaTwilio(
            exito=True,
            sid=message.sid,
            status=message.status,
            error_code=None,
            error_message=None,
        )

    except TwilioRestException as e:
        print(f"Error de Twilio al enviar mensaje: {e.code}")
        return RespuestaTwilio(
            exito=False,
            sid=None,
            status="failed",
            error_code=e.status,
            error_message=e.msg,
        )
    except (ConnectionError, Timeout) as e:
        print(f"Error de conexión al enviar mensaje: {e}")
        return RespuestaTwilio(
            exito=False,
            sid=None,
            status="failed",
            error_code=None,
            error_message=str(e),
        )
