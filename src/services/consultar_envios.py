import logging

import pandas as pd
from rich.align import Align
from rich.console import Console, Group
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt

from src.config import settings
from src.database.repository import (
    exportar_no_entregados_a_excel,
    obtener_registros_por_semana,
)
from src.utils.limpiar_pantalla import limpiar_pantalla

console = Console()

logger = logging.getLogger(__name__)


def consultar_envios():
    limpiar_pantalla()

    # Banner con arte ASCII de BD
    db_ascii = """
   .----------------.
  | .--------------. |
  | |  ____  ____  | |
  | | |_  _||_  _| | |
  | |   ||    ||   | |
  | |  _||_  _||_  | |
  | | |____||____| | |
  | |              | |
  | '--------------' |
   '----------------'
  /==================\\
 | [O]  DATABASE  [O] |
  \\==================/
    """

    contenido_banner = Group(
        Align.center(f"[bold magenta]{db_ascii}[/bold magenta]"),
        Align.center(
            "[bold magenta]CONSULTA DE ENVIOS EN BASE DE DATOS[/bold magenta]\n"
        ),
        Align.center(
            "[dim white]Exporta un Excel directo de SQLite con el historial o los pendientes.[/dim white]"
        ),
    )

    console.print(
        Panel(
            contenido_banner,
            expand=False,
            border_style="magenta",
            padding=(1, 2),
        )
    )

    semana_actual = settings.FECHA_ACTUAL.isocalendar().week

    semana = IntPrompt.ask(
        "\n[bold magenta]¿De qué semana deseas consultar los envíos de cupones?[/bold magenta]",
        default=semana_actual,
    )

    canal = Prompt.ask(
        "\n[bold magenta]¿De qué canal deseas consultar? (twilio o correo)[/bold magenta]",
        default="twilio",
    )

    tipo_consulta = Prompt.ask(
        "\n[bold magenta]¿Qué tipo de reporte deseas generar? (todos / pendientes)[/bold magenta]",
        choices=["todos", "pendientes"],
        default="todos",
    )

    console.print(
        f"\n[magenta]🔍 Leyendo registros de la base de datos para la semana {semana} ({canal} - {tipo_consulta})...[/magenta]"
    )

    try:
        # Lógica combinada de consulta
        if tipo_consulta == "pendientes":
            df: pd.DataFrame = exportar_no_entregados_a_excel(semana)
            nombre_archivo = f"cupones_pendientes_{canal}_semana_{semana}.xlsx"
        else:
            df: pd.DataFrame = obtener_registros_por_semana(semana, canal)
            nombre_archivo = f"cupones_enviados_{canal}_semana_{semana}.xlsx"

        if df.empty:
            console.print(
                f"\n[bold yellow]⚠ No hay registros ({tipo_consulta}) en la semana {semana} para el canal {canal}.[/bold yellow]"
            )
            input("\nPresiona ENTER para continuar...")
            return

        # Generar archivo en carpeta 'reportes'
        archivo_excel = settings.BASE_DIR / "reportes" / nombre_archivo
        archivo_excel.parent.mkdir(parents=True, exist_ok=True)

        df.to_excel(archivo_excel, index=False, engine="openpyxl")

        console.print(
            Panel(
                f"[bold green]✔ Reporte de BD generado con éxito[/bold green]\n\n"
                f"📊 [white]Registros encontrados:[/white] {len(df)}\n"
                f"📄 [white]Archivo:[/white] {archivo_excel.name}\n"
                f"📍 [white]Ruta:[/white] {archivo_excel}",
                border_style="green",
            )
        )

    except ValueError as e:
        console.print(f"[red]❌ Error al consultar la base de datos: {e}[/red]")
    except PermissionError:
        console.print(
            "[red]❌ Error: Cierra el archivo Excel antes de continuar.[/red]"
        )
    except Exception as e:
        console.print(f"[red]❌ Error inesperado: {e}[/red]")
        logger.exception(f"Error inesperado al consultar la base de datos: {e}")

    input("\nPresiona ENTER para continuar...")
