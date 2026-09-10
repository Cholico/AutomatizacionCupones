import logging
from pathlib import Path

import qrcode
from PIL import Image
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer

from src.config import settings

logger = logging.getLogger(__name__)


class QRGenerationError(Exception):
    pass


def create_qr(id_emp: str, nombre: str, codigo: str) -> Path:
    try:
        qr = qrcode.QRCode(
            version=1, error_correction=qrcode.ERROR_CORRECT_H, box_size=10, border=4
        )

        qr.add_data(codigo)
        qr.make(fit=True)

        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer(),
            color_mask=SolidFillColorMask(
                back_color=(255, 255, 255), front_color=(31, 126, 211)
            ),
        ).convert("RGB")

        # Procesar logo
        logo = Image.open(
            settings.BASE_DIR / "src" / "assets" / "img" / "dolphy_logo.png"
        ).convert("RGBA")

        # 1. Obtener dimensiones originales
        orig_w, orig_h = logo.size
        base_w, base_h = img.size

        # 2. Definir el tamaño máximo que puede tener (el ancho del QR // 4)
        max_size = base_w // 4

        # 3. Calcular nuevas dimensiones manteniendo la proporción
        if orig_w > orig_h:
            # Si es más ancho que alto
            new_w = max_size
            new_h = int(max_size * orig_h / orig_w)
        else:
            # Si es más alto que ancho (o cuadrado perfecto)
            new_h = max_size
            new_w = int(max_size * orig_w / orig_h)
        logo = logo.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # Centrar y pegar
        pos = ((base_w - new_w) // 2, (base_h - new_h) // 2)
        mask = logo if logo.mode == "RGBA" else None
        img.paste(logo, pos, mask)

        # 5. Guardado (Asegurando que la carpeta exista)
        output_dir = (
            settings.BASE_DIR
            / "qr_generados"
            / f"qr_generados_sem_{settings.FECHA_ACTUAL.isocalendar().week}_{settings.FECHA_ACTUAL.year}"
        )
        output_dir.mkdir(parents=True, exist_ok=True)  # Crea la carpeta si no existe

        qr_name = f"{id_emp}_{nombre}_cupon_dolphy.png"
        img.save(output_dir / qr_name)

        return output_dir / qr_name

    except FileNotFoundError as e:
        logger.error(f"Error al no encontrar el archivo: {e}")
        raise FileNotFoundError(f"Archivo no encontrado: {e}")
    except PermissionError:
        logger.error(f"Error de permisos: No se puede escribir en {output_dir}")
        raise PermissionError(f"No se puede escribir en {output_dir}")
    except Exception:
        logger.exception(f"Error inesperado generando QR para {id_emp}")
        raise QRGenerationError(f"Error inesperado generando QR para {id_emp}")
