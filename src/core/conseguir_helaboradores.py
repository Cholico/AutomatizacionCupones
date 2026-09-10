from pathlib import Path

import pandas as pd

from src.config import settings


def conseguir_helaboradores(archivo: str, tipo_envio: str) -> pd.DataFrame:
    archivo_path = Path(archivo)

    # Si no tiene extensión, asumimos .xlsx
    if not archivo_path.suffix:
        archivo_path = archivo_path.with_suffix(".xlsx")

    # Solo permitimos archivos modernos de Excel
    if archivo_path.suffix.lower() != ".xlsx":
        raise ValueError(
            f"Formato no permitido: {archivo_path.suffix}. Se esperaba un archivo .xlsx"
        )

    # Garantizar compatibilidad si pasan una ruta absoluta o relativa
    if not archivo_path.is_absolute():
        archivo_path = settings.BASE_DIR / archivo_path

    if not archivo_path.exists():
        raise FileNotFoundError(f"El archivo {archivo_path} no existe.")

    try:
        # Leemos todo como string inicialmente para no perder ceros a la izquierda
        df = pd.read_excel(
            archivo_path,
            dtype=str,
            engine="openpyxl",
        )

        if df.empty:
            raise RuntimeError(f"El archivo {archivo_path} está vacío.")

        # Normalizar nombres de columnas (quitar espacios y convertir a minúsculas)
        df.columns = df.columns.str.strip().str.lower()

        # 1. Validar columnas base obligatorias
        columnas_base = {"id", "nombre", "tienda", "codigo"}
        columnas_presentes = set(df.columns)

        faltantes_base = columnas_base - columnas_presentes
        if faltantes_base:
            raise ValueError(
                f"Faltan columnas obligatorias en el archivo Excel: {', '.join(faltantes_base)}"
            )

        # 2. Validar según el canal de envío
        tiene_telefono = "telefono" in columnas_presentes
        tiene_correo = "correo" in columnas_presentes

        if tipo_envio == "correo" and not tiene_correo:
            raise ValueError(
                "El archivo Excel no contiene la columna obligatoria 'correo'."
            )

        if tipo_envio == "twilio" and not tiene_telefono:
            raise ValueError(
                "El archivo Excel no contiene la columna obligatoria 'telefono'."
            )

        # Rellenar valores nulos con string vacío para evitar flotantes NaN
        df = df.fillna("")

        # Normalizar datos base
        df["codigo"] = df["codigo"].astype(str).str.strip()

        # Normalización segura de 'telefono' (elimina .0 si Excel lo interpreta como float)
        if tiene_telefono:
            df["telefono"] = (
                df["telefono"]
                .astype(str)
                .str.strip()
                .str.replace(r"\.0$", "", regex=True)
                .str.replace(" ", "", regex=True)
            )
        else:
            df["telefono"] = ""

        # Normalización segura de 'correo'
        if tiene_correo:
            df["correo"] = df["correo"].astype(str).str.strip()
        else:
            df["correo"] = ""

        return df

    except ValueError as e:
        raise ValueError(f"Error en la estructura del Excel: {e}") from e
    except pd.errors.ParserError as e:
        raise RuntimeError(
            f"El archivo {archivo_path} no contiene datos válidos: {e}"
        ) from e
