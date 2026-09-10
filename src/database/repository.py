import pandas as pd

from src.database.connection import obtener_conexion
from src.schemas.schemas import MensajeCorreo, MensajeTwilio


def guardar_envio_twilio(mensaje: MensajeTwilio) -> int:
    """Inserta un registro de intento de envío por WhatsApp (Twilio) en la BD."""
    query = """
        INSERT INTO envios_twilio (
            id_emp, codigo, nombre, tienda, telefono, producto, 
            fecha_vencimiento, semana, estatus, sid, motivo
        ) VALUES (
            :id_emp, :codigo, :nombre, :tienda, :telefono, :producto, 
            :fecha_vencimiento, :semana, :estatus, :sid, :motivo
        )
    """
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        # model_dump() convierte el esquema de Pydantic a un diccionario directo para SQL
        cursor.execute(query, mensaje.model_dump())
        conn.commit()

        if cursor.lastrowid is None:
            raise RuntimeError("No se pudo obtener el ID del registro insertado.")

        return cursor.lastrowid


def guardar_envio_correo(mensaje: MensajeCorreo) -> int:
    """Inserta un registro de intento de envío por Correo en la BD."""
    query = """
        INSERT INTO envios_correo (
            id_emp, codigo, nombre, tienda, correo, producto, 
            fecha_vencimiento, semana, estatus, motivo
        ) VALUES (
            :id_emp, :codigo, :nombre, :tienda, :correo, :producto, 
            :fecha_vencimiento, :semana, :estatus, :motivo
        )
    """
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(query, mensaje.model_dump())
        conn.commit()

        if cursor.lastrowid is None:
            raise RuntimeError("No se pudo obtener el ID del registro insertado.")

        return cursor.lastrowid


def obtener_registros_por_semana(semana: int, canal: str = "twilio") -> pd.DataFrame:
    """Consulta rápida para auditoría de registros con errores en una semana específica."""
    if canal == "twilio":
        tabla = "envios_twilio"
    elif canal == "correo":
        tabla = "envios_correo"
    else:
        raise ValueError("Canal no válido. Debe ser 'twilio' o 'correo'.")

    query = f"SELECT * FROM {tabla} WHERE semana = ? ORDER BY id DESC"

    with obtener_conexion() as conn:
        df = pd.read_sql_query(query, conn, params=(semana,))

    if df.empty:
        raise ValueError(f"No se encontraron registros para la semana {semana}.")

    return df


def exportar_no_entregados_a_excel(semana: int) -> pd.DataFrame:
    """
    Busca envíos de WhatsApp de una semana específica cuyo estatus
    NO sea 'delivered' ni 'read' y los guarda en Excel.
    """
    query = """
        SELECT 
            id_emp AS "Id",
            codigo AS "Codigo",
            nombre AS "Empleado",
            tienda AS "Tienda",
            telefono AS "Teléfono",
            producto AS "Producto",
            fecha_vencimiento AS "Vencimiento",
            estatus AS "Estatus Twilio",
            sid AS "SID",
            motivo AS "Detalle Error",
            fecha_registro AS "Fecha Registro"
        FROM envios_twilio
        WHERE semana = ?
        ORDER BY id DESC
    """
    with obtener_conexion() as conn:
        df = pd.read_sql_query(query, conn, params=(semana,))

    if df.empty:
        raise ValueError(f"No se encontraron registros para la semana {semana}.")

    return df
