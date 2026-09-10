import logging
import queue
import time

import pandas as pd
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)

from src.config import settings
from src.database.repository import guardar_envio_twilio, obtener_registros_por_semana
from src.schemas.schemas import (
    MensajeTwilio,
    RespuestaTwilio,
    configuracion_envio,
    payload_cupon,
)
from src.twilio.github_service import upload_to_github
from src.twilio.twilio_service import enviar_mensaje_por_whatsapp

console = Console()
logger = logging.getLogger(__name__)


def worker_envios_twilio(
    cola_envio: queue.Queue,
    total: int,
    configuracion_de_envio: configuracion_envio,
):

    enviados = 0
    errores = 0
    contador_lote = 0
    numero_lote = 1
    inicio_lote = time.time()

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TextColumn("Enviados: {task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Enviando WhatsApps...", total=total)

        while True:
            payload: payload_cupon = cola_envio.get()

            if payload is None:
                cola_envio.task_done()
                break

            try:
                try:
                    link = upload_to_github(ruta_qr=payload.qr_path)
                except Exception as e_github:
                    link = None
                    logger.error(
                        f"Error de red/servidor al subir imagen a GitHub para {payload.nombre}: {e_github}"
                    )

                logger.info(f"Imagen subida a GitHub para {payload.nombre}: {link}")

                if not link:
                    registro = MensajeTwilio(
                        id_emp=payload.id_emp,
                        codigo=payload.codigo,
                        nombre=payload.nombre,
                        tienda=payload.tienda,
                        telefono=payload.telefono,
                        producto=payload.producto,
                        fecha_vencimiento=payload.fecha_vencimiento,
                        estatus="error",
                        semana=settings.FECHA_ACTUAL.isocalendar().week,
                        sid=None,
                        motivo="No se pudo subir la imagen al servicio de GitHub",
                    )
                    guardar_envio_twilio(registro)

                    errores += 1
                    logger.error(
                        f"No se pudo subir la imagen a GitHub para {payload.nombre}"
                    )
                    continue

                respuesta_twilio: RespuestaTwilio = enviar_mensaje_por_whatsapp(
                    link_img=link,
                    telefono=payload.telefono,
                    empleado=payload.nombre,
                    fecha_vencimiento=payload.fecha_vencimiento,
                    producto=payload.producto,
                )

                if not respuesta_twilio.exito:
                    registro = MensajeTwilio(
                        id_emp=payload.id_emp,
                        codigo=payload.codigo,
                        nombre=payload.nombre,
                        tienda=payload.tienda,
                        telefono=payload.telefono,
                        producto=payload.producto,
                        fecha_vencimiento=payload.fecha_vencimiento,
                        estatus="failed",
                        semana=settings.FECHA_ACTUAL.isocalendar().week,
                        sid=respuesta_twilio.sid or None,
                        motivo=respuesta_twilio.error_message
                        or "Error desconocido al enviar mensaje por Twilio",
                    )
                    guardar_envio_twilio(registro)
                    errores += 1
                else:
                    try:
                        registro = MensajeTwilio(
                            id_emp=payload.id_emp,
                            codigo=payload.codigo,
                            nombre=payload.nombre,
                            tienda=payload.tienda,
                            telefono=payload.telefono,
                            producto=payload.producto,
                            fecha_vencimiento=payload.fecha_vencimiento,
                            estatus="delivered",
                            semana=settings.FECHA_ACTUAL.isocalendar().week,
                            sid=respuesta_twilio.sid or None,
                            motivo="OK",
                        )
                        guardar_envio_twilio(registro)
                        enviados += 1
                    except Exception as e:
                        logger.exception(
                            f"Error guardando envío de Twilio para {payload.nombre}: {e}"
                        )
                        registro = MensajeTwilio(
                            id_emp=payload.id_emp,
                            codigo=payload.codigo,
                            nombre=payload.nombre,
                            tienda=payload.tienda,
                            telefono=payload.telefono,
                            producto=payload.producto,
                            fecha_vencimiento=payload.fecha_vencimiento,
                            estatus="failed",
                            semana=settings.FECHA_ACTUAL.isocalendar().week,
                            sid=respuesta_twilio.sid or None,
                            motivo=respuesta_twilio.error_message
                            or "Error desconocido al enviar mensaje por Twilio",
                        )
                        guardar_envio_twilio(registro)
                        errores += 1

                # Espera normal entre mensajes
                time.sleep(configuracion_de_envio.espera_mensaje)

            except Exception as e:
                logger.exception(
                    f"Error procesando envío WhatsApp para {payload.nombre}: {e}"
                )
                errores += 1

                registro = MensajeTwilio(
                    id_emp=payload.id_emp,
                    codigo=payload.codigo,
                    nombre=payload.nombre,
                    tienda=payload.tienda,
                    telefono=payload.telefono,
                    producto=payload.producto,
                    fecha_vencimiento=payload.fecha_vencimiento,
                    estatus="failed",
                    semana=settings.FECHA_ACTUAL.isocalendar().week,
                    sid=None,
                    motivo=f"Error inesperado / conexion: {e}",
                )
                guardar_envio_twilio(registro)

            finally:
                progress.update(task, advance=1)
                cola_envio.task_done()

                if payload is not None:
                    contador_lote += 1

                    if contador_lote >= configuracion_de_envio.tamano_lote:
                        tiempo_transcurrido = time.time() - inicio_lote

                        if tiempo_transcurrido < configuracion_de_envio.espera_lote:
                            tiempo_espera = (
                                configuracion_de_envio.espera_lote - tiempo_transcurrido
                            )
                            console.print(
                                f"\n[yellow]⏳ Lote {numero_lote} completado. Esperando {int(tiempo_espera)} segundos...[/yellow]"
                            )
                            time.sleep(tiempo_espera)

                        contador_lote = 0
                        numero_lote += 1
                        inicio_lote = time.time()

    console.print(f"\n[green]✔ Enviados correctamente:[/green] {enviados}")
    console.print(f"[red]✖ Errores:[/red] {errores}\n")

    df_reporte: pd.DataFrame = obtener_registros_por_semana(
        semana=settings.FECHA_ACTUAL.isocalendar().week, canal="twilio"
    )

    if not df_reporte.empty:
        semana = settings.FECHA_ACTUAL.isocalendar().week
        nombre = f"cupones_whatsapp_enviados_semana_{semana}.xlsx"

        carpeta_reportes = settings.BASE_DIR / "reportes"
        carpeta_reportes.mkdir(parents=True, exist_ok=True)
        try:
            df_reporte.to_excel(carpeta_reportes / nombre, index=False)
        except PermissionError:
            console.print(
                f"[red]No se pudo guardar el reporte '{nombre}' porque está abierto en otra aplicación.[/red]"
            )
        console.print(
            f"[yellow]Reporte consolidado de envíos generado:[/yellow] {nombre}"
        )
    else:
        console.print(
            f"[yellow]No se generó reporte consolidado de envíos, no hay registros para la semana {settings.FECHA_ACTUAL.isocalendar().week}.[/yellow]"
        )
