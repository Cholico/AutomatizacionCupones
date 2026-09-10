import base64
import logging
import mimetypes
from pathlib import Path

import requests
from requests.exceptions import ConnectionError, Timeout

from src.config import settings
from src.core.mensaje_correo import MENSAJE_CORREO
from src.graph.auth import obtener_token
from src.schemas.schemas import GraphAccessTokenResponse, payload_cupon

logger = logging.getLogger(__name__)


class EnvioCorreoError(Exception):
    pass


def adjuntar(ruta: Path, content_id: str = "qr_image_cid") -> dict:
    if not ruta.exists():
        raise FileNotFoundError(f"No existe el archivo: {ruta}")

    tipo_contenido, _ = mimetypes.guess_type(ruta.name)
    tipo_contenido = tipo_contenido or "application/octet-stream"

    contenido_base64 = base64.b64encode(ruta.read_bytes()).decode("utf-8")

    return {
        "@odata.type": "#microsoft.graph.fileAttachment",
        "name": ruta.name,
        "contentType": tipo_contenido,
        "contentBytes": contenido_base64,
        "isInline": True,  # Indicar a Graph API que va dentro del cuerpo HTML
        "contentId": content_id,  # Coincide con <img src="cid:qr_image_cid">
    }


def enviar_correo(
    payload_cupon: payload_cupon,
    asunto: str,
) -> None:

    try:
        graph_response: GraphAccessTokenResponse = obtener_token()

        remitente = settings.SENDER_EMAIL

        mensaje = MENSAJE_CORREO.substitute(
            nombre=payload_cupon.nombre,
            producto=payload_cupon.producto,
            fecha_vigencia=payload_cupon.fecha_vencimiento,
        )

        # 1. Asegurar formato correcto de destinatario para Graph API
        to_recipients = [{"emailAddress": {"address": payload_cupon.correo.strip()}}]

        # 2. Asegurar que attachments sea una lista [dict] y no un dict solo
        adjuntos = []
        if payload_cupon.qr_path:
            adjuntos.append(adjuntar(payload_cupon.qr_path, content_id="qr_image_cid"))

        payload = {
            "message": {
                "subject": asunto,
                "body": {
                    "contentType": "HTML",
                    "content": mensaje,
                },
                "toRecipients": to_recipients,
                "attachments": adjuntos,
            },
            "saveToSentItems": True,  # Debe ser boolean True (no string)
        }

        respuesta = requests.post(
            f"https://graph.microsoft.com/v1.0/users/{remitente}/sendMail",
            headers={
                "Authorization": f"Bearer {graph_response.access_token}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=60,
        )

        if respuesta.status_code != 202:
            logger.error(f"Error {respuesta.status_code}: {respuesta.text}")
            raise EnvioCorreoError(f"Error al enviar correo: {respuesta.text}")

        logger.info(f"Correo enviado a {payload_cupon.correo} con asunto '{asunto}'")

    except RuntimeError as e:
        logger.error(f"Error al obtener token de Graph: {e}")
        raise EnvioCorreoError(f"Error al obtener token de Graph: {e}")
    except (ConnectionError, Timeout) as e:
        logger.error(f"Error de conexión al enviar correo: {e}")
        raise EnvioCorreoError(f"Error de conexión al enviar correo: {e}")
