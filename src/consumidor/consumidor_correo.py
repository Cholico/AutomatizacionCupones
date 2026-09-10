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
from src.database.repository import guardar_envio_correo, obtener_registros_por_semana
from src.graph.enviar_correos import enviar_correo
from src.schemas.schemas import (
    MensajeCorreo,  # O tu esquema de reporte homologado
    configuracion_envio,
    payload_cupon,
)

console = Console()
logger = logging.getLogger(__name__)


def worker_envios_correo(
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
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TextColumn("Enviados: {task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Enviando correos...", total=total)

        while True:
            payload: payload_cupon = cola_envio.get()

            if payload is None:
                cola_envio.task_done()
                break

            try:
                try:
                    enviar_correo(
                        payload_cupon=payload,
                        asunto="Tu cupón de Helados Dolphy",
                    )
                    enviados += 1

                    registro = MensajeCorreo(
                        id_emp=payload.id_emp,
                        codigo=payload.codigo,
                        nombre=payload.nombre,
                        tienda=payload.tienda,
                        correo=payload.correo,
                        producto=payload.producto,
                        fecha_vencimiento=payload.fecha_vencimiento,
                        estatus="sent",
                        semana=settings.FECHA_ACTUAL.isocalendar().week,
                        motivo="OK",
                    )
                    guardar_envio_correo(registro)

                except Exception as e:
                    errores += 1
                    logger.error(f"Error enviando correo a {payload.nombre}: {e}")

                    registro = MensajeCorreo(
                        id_emp=payload.id_emp,
                        codigo=payload.codigo,
                        nombre=payload.nombre,
                        tienda=payload.tienda,
                        correo=payload.correo,
                        producto=payload.producto,
                        fecha_vencimiento=payload.fecha_vencimiento,
                        estatus="failed",
                        semana=settings.FECHA_ACTUAL.isocalendar().week,
                        motivo=f"Error enviando correo a {payload.nombre}: {e}",
                    )
                    guardar_envio_correo(registro)

                # Espera normal entre mensajes
                time.sleep(configuracion_de_envio.espera_mensaje)

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
        semana=settings.FECHA_ACTUAL.isocalendar().week, canal="correo"
    )

    if not df_reporte.empty:
        semana = settings.FECHA_ACTUAL.isocalendar().week
        nombre = f"correos_enviados_semana_{semana}.xlsx"

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
