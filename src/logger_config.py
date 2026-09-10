import logging
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from src.config import settings


def configurar_logging(
    directorio_logs: str = "logs",
) -> tuple[logging.Logger, Path]:
    
    # Resolver la ruta de logs combinando con BASE_DIR si es relativa
    logs = Path(directorio_logs)
    if not logs.is_absolute():
        logs = settings.BASE_DIR / logs

    logs.mkdir(parents=True, exist_ok=True)

    fecha_ejecucion = datetime.now(ZoneInfo("America/Mexico_City")).strftime(
        "%Y%m%d_%H%M%S"
    )

    ruta_log = logs / f"proceso_reportes_{fecha_ejecucion}.log"
    ruta_errores = logs / f"errores_{fecha_ejecucion}.log"

    formato = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 1. Consola
    handler_consola = logging.StreamHandler()
    handler_consola.setLevel(logging.INFO)
    handler_consola.setFormatter(formato)

    # 2. Archivo general
    handler_archivo = logging.FileHandler(ruta_log, encoding="utf-8")
    handler_archivo.setLevel(logging.INFO)
    handler_archivo.setFormatter(formato)

    # 3. Archivo de errores
    handler_errores = logging.FileHandler(ruta_errores, encoding="utf-8")
    handler_errores.setLevel(logging.ERROR)
    handler_errores.setFormatter(formato)

    # Logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Limpiar handlers previos para evitar logs duplicados
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Suscribir handlers
    root_logger.addHandler(handler_archivo)
    root_logger.addHandler(handler_errores)

    logging.getLogger("twilio.http_client").setLevel(logging.WARNING)

    return root_logger, ruta_log