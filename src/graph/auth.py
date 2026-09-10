import logging

import msal
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.config import settings
from src.schemas.schemas import GraphAccessTokenResponse

logger = logging.getLogger(__name__)


# 1. Crear una sesión HTTP con reintentos para MSAL
def _crear_sesion_http() -> requests.Session:
    session = requests.Session()
    retries = Retry(
        total=3,  # Reintentar hasta 3 veces
        backoff_factor=1,  # Espera 1s, 2s, 4s entre reintentos
        status_forcelist=[500, 502, 503, 504],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    return session


# 2. Instanciar la app a nivel global para aprovechar el CACHÉ interno de MSAL
_app_msal = msal.ConfidentialClientApplication(
    client_id=settings.CLIENT_ID,
    authority=f"https://login.microsoftonline.com/{settings.TENANT_ID}",
    client_credential=settings.CLIENT_SECRET,
    http_client=_crear_sesion_http(),  # Inyectamos la sesión con reintentos
)


def obtener_token() -> GraphAccessTokenResponse:
    # 1. Intentar obtener el token desde la caché interna de MSAL
    datos_token = _app_msal.acquire_token_silent(
        scopes=["https://graph.microsoft.com/.default"], account=None
    )

    # 2. Si no está en caché, solicitar uno nuevo mediante flujo App-Only
    if not datos_token:
        logger.info("Solicitando nuevo token de Microsoft Graph")
        datos_token = _app_msal.acquire_token_for_client(
            scopes=["https://graph.microsoft.com/.default"],
            timeout=15,
        )

    # 3. Validar con isinstance() para asegurar que es un diccionario
    # Esto elimina el error de Pylance al garantizar que 'datos_token' NO es None
    # 3. Validar si la respuesta contiene errores
    if not isinstance(datos_token, dict) or "access_token" not in datos_token:
        # En caso de error, aseguramos la conversión a dict para usar .get()
        error_info = datos_token if isinstance(datos_token, dict) else {}
        error_msg = error_info.get("error_description", str(datos_token))

        logger.error("No se pudo obtener el token | error=%s", error_msg)
        raise RuntimeError(f"Error de MSAL: {error_msg}")

    logger.info(
        "Token obtenido correctamente | vigencia_segundos=%s",
        datos_token.get("expires_in"),
    )

    # 4. Validar e instanciar el modelo de Pydantic con el diccionario de MSAL
    return GraphAccessTokenResponse.model_validate(datos_token)
