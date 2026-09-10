import logging

import pandas as pd
from rich.align import Align
from rich.console import Console, Group
from rich.panel import Panel
from rich.prompt import IntPrompt

from src.config import settings
from src.database.repository import exportar_no_entregados_a_excel
from src.twilio.twilio_consulta import verificar_estatus_real_twilio
from src.utils.limpiar_pantalla import limpiar_pantalla

console = Console()

logger = logging.getLogger(__name__)

def consultar_twilio():
    limpiar_pantalla()

    # Arte ASCII de Twilio en color rojo
    twilio_ascii = """
 _____               _ _ _       
|_   _|             (_) (_)      
  | | ___      _____| |_  ___    
  | |/ _ \    / / _ \ | |/ _ \   
  | | (_) |  / /  __/ | | (_) |  
  \_/\___/  /_/ \___|_|_|\___/   
    """

    contenido_banner = Group(
        Align.center(f"[bold red]{twilio_ascii}[/bold red]"),
        Align.center("[bold red]Reporte de Mensajes WhatsApp No Entregados[/bold red]\n"),
        Align.center("[dim white]Filtra por semana y genera un reporte en Excel de envíos pendientes o fallidos.[/dim white]"),
    )

    console.print(
        Panel(
            contenido_banner,
            expand=False,
            border_style="red",
            padding=(1, 2),
        )
    )

    semana_actual = settings.FECHA_ACTUAL.isocalendar().week

    semana = IntPrompt.ask(
        "\n[bold red]¿De qué semana deseas consultar los mensajes?[/bold red]",
        default=semana_actual,
    )

    console.print(
        f"\n[red]🔍 Consultando base de datos para la semana {semana}...[/red]"
    )

    try:
        df: pd.DataFrame = exportar_no_entregados_a_excel(semana)

        df_mensajes_no_entregados = verificar_estatus_real_twilio(df_mensajes=df)

        archivo_excel = (
            settings.BASE_DIR
            / "reportes"
            / f"cupones_whatsapp_no_entregados_semana_{semana}.xlsx"
        )

        archivo_excel.parent.mkdir(parents=True, exist_ok=True)

        df_mensajes_no_entregados.to_excel(
            archivo_excel, index=False, engine="openpyxl"
        )

        console.print(
            Panel(
                f"[bold green]✔ Reporte de Twilio generado con éxito[/bold green]\n\n"
                f"📊 [white]Registros no entregados:[/white] {len(df_mensajes_no_entregados)}\n"
                f"📄 [white]Archivo:[/white] {archivo_excel.name}\n"
                f"📍 [white]Ruta:[/white] {archivo_excel}",
                border_style="green",
            )
        )

    except ValueError as e:
        console.print(f"[red]❌ Error al generar el reporte: {e}[/red]")
    except PermissionError:
        console.print(
            "[red]❌ Error: Cierra el archivo Excel antes de continuar.[/red]"
        )
    except Exception as e:
        console.print(f"[red]❌ Error inesperado: {e}[/red]")
        logger.exception(f"Error inesperado al consultar Twilio: {e}")

    input("\nPresiona ENTER para continuar...")