import logging
import queue
import threading

import pandas as pd
from rich.console import Console
from rich.prompt import Confirm

from src.cli.envio_cupones_ui import mostrar_encabezado
from src.cli.prompts import (
    pedir_archivo,
    pedir_configuracion_envio,
    pedir_fecha_vencimiento,
    pedir_producto,
)
from src.config import settings
from src.consumidor.consumidor_correo import worker_envios_correo
from src.consumidor.consumidor_twilio import worker_envios_twilio
from src.core.conseguir_helaboradores import conseguir_helaboradores
from src.core.generador_qr import QRGenerationError, create_qr
from src.database.repository import guardar_envio_correo, guardar_envio_twilio
from src.schemas.schemas import (
    MensajeCorreo,
    MensajeTwilio,
    configuracion_envio,
    payload_cupon,
)
from src.utils.limpiar_pantalla import limpiar_pantalla
from src.utils.validar_correo import es_correo_valido
from src.utils.validar_telefono import es_telefono_valido

logger = logging.getLogger(__name__)

console = Console()


def envio_cupones(tipo_envio: str = "correo"):

    limpiar_pantalla()
    # Mostrar encabezado
    mostrar_encabezado(tipo_envio=tipo_envio)

    # Pedir archivo de empleados
    archivo_empleados = pedir_archivo()

    # Bucle de reintento para carga y validación del Excel
    while True:
        try:
            df_emp = conseguir_helaboradores(
                archivo=archivo_empleados, tipo_envio=tipo_envio
            )
            df_emp = df_emp.fillna("N/A")
            break  # Si se lee con éxito, sale del bucle y continúa la ejecución

        except (ValueError, FileNotFoundError, RuntimeError) as e:
            console.print(f"\n[bold red]❌ Error de validación:[/bold red] {e}\n")

            # Pregunta al usuario si desea reintentar tras corregir el archivo
            reintentar = Confirm.ask(
                "[bold yellow]¿Deseas editar el archivo Excel y volver a intentarlo?[/bold yellow]",
                default=True,
            )

            if not reintentar:
                console.print("\n[cyan]Proceso cancelado por el usuario.[/cyan]\n")
                return  # Regresa al menú principal limpiamente

    # 2. Configuración del usuario
    fecha_vencimiento = pedir_fecha_vencimiento()
    producto = pedir_producto()

    # Pedir configuracion avanzada del usuarios sobre envios
    configuracion_de_envio: configuracion_envio = pedir_configuracion_envio()

    # Crear cola
    cola_envio = queue.Queue()

    # total de cupones a enviar
    total = len(df_emp)

    # Eligir el worker según el tipo de envío
    if tipo_envio == "correo":
        worker_envios = worker_envios_correo
    elif tipo_envio == "twilio":
        worker_envios = worker_envios_twilio
    else:
        raise ValueError("Tipo de envío no válido. Debe ser 'correo' o 'twilio'.")

    # 5. Crear worker
    hilo = threading.Thread(
        target=worker_envios,
        args=(cola_envio, total, configuracion_de_envio),
    )

    hilo.start()

    registros_omitidos = 0

    # Generar cupones
    for _, row in df_emp.iterrows():
        # Obtener valores opcionales de forma segura
        val_telefono = (
            str(row["telefono"]).strip()
            if "telefono" in row and pd.notna(row["telefono"])
            else ""
        )
        val_correo = (
            str(row["correo"]).strip()
            if "correo" in row and pd.notna(row["correo"])
            else ""
        )

        telefono_limpio = (
            "" if val_telefono in ("N/A", "nan", "None", "") else val_telefono
        )
        correo_limpio = "" if val_correo in ("N/A", "nan", "None", "") else val_correo

        # Validar disponibilidad y formato de correo según canal
        if tipo_envio == "correo" and (
            not correo_limpio or not es_correo_valido(correo_limpio)
        ):
            logger.warning(
                f"Omitido ID {row['id']}: Correo no válido o ausente ('{correo_limpio}')."
            )

            # Guardar omisión en BD
            guardar_envio_correo(
                MensajeCorreo(
                    id_emp=str(row["id"]),
                    codigo=str(row["codigo"]),
                    nombre=row["nombre"],
                    tienda=row["tienda"],
                    correo=correo_limpio,
                    producto=producto,
                    fecha_vencimiento=fecha_vencimiento,
                    estatus="failed",
                    semana=settings.FECHA_ACTUAL.isocalendar().week,
                    motivo="Datos invalidos o ausentes: Correo no válido o ausente",
                )
            )

            registros_omitidos += 1
            continue

        if tipo_envio == "twilio" and not es_telefono_valido(telefono_limpio):
            logger.warning(f"Omitido ID {row['Id']}: Teléfono no válido.")
            # Guardar omisión en BD
            guardar_envio_twilio(
                MensajeTwilio(
                    id_emp=str(row["id"]),
                    codigo=str(row["codigo"]),
                    nombre=row["nombre"],
                    tienda=row["tienda"],
                    telefono=telefono_limpio,
                    producto=producto,
                    fecha_vencimiento=fecha_vencimiento,
                    estatus="failed",
                    semana=settings.FECHA_ACTUAL.isocalendar().week,
                    sid=None,
                    motivo="Sin teléfono válido",
                )
            )
            registros_omitidos += 1
            continue

        try:
            # Generar QR
            qr_path = create_qr(
                id_emp=str(row["id"]),
                nombre=row["nombre"],
                codigo=str(row["codigo"]),
            )

            payload = payload_cupon(
                qr_path=qr_path,
                nombre=row["nombre"],
                telefono=telefono_limpio,
                correo=correo_limpio,
                codigo=str(row["codigo"]),
                tienda=row["tienda"],
                producto=producto,
                fecha_vencimiento=fecha_vencimiento,
                id_emp=str(row["id"]),
            )

        except QRGenerationError as e:
            logger.error(f"Error generando QR para {row['nombre']}: {e}")
            continue

        if payload:
            cola_envio.put(payload)

    # 6. Avisar al consumidor que terminamos
    cola_envio.put(None)

    # 7. Esperar a que termine
    hilo.join()
