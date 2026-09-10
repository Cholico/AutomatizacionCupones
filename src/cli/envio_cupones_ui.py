from rich.align import Align
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table

console = Console()


def mostrar_encabezado(tipo_envio: str):
    # Banner ASCII limpio y directo
    logo_ascii = """
  ____   ____  _     ____  _   _ __   __
 |  _ \ / __ \| |   |  _ \| | | |\ \ / /
 | | | | |  | | |   | |_) | |_| | \ V / 
 | |_| | |__| | |___|  __/|  _  |  | |  
 |____/ \____/|_____|_|   |_| |_|  |_|  
    """

    titulo_texto = (
        f"[bold cyan]{logo_ascii}[/bold cyan]\n"
        f"[bold white]DOLPHY CUPONES ({tipo_envio.upper()})[/bold white]\n"
        "[dim white]Generador y envío de cupones a Helaboradores[/dim white]"
    )

    contenido = Group(
        Align.center(titulo_texto),
    )

    console.print(
        Panel(
            contenido,
            border_style="cyan",
            padding=(1, 4),
        )
    )


def mostrar_configuracion(
    archivo: str,
    producto: str,
    dias: int,
    total: int,
):
    tabla = Table(
        show_header=False,
        box=None,
        padding=(0, 2),
    )

    tabla.add_column(style="bold cyan")
    tabla.add_column(style="white")

    tabla.add_row("Archivo", archivo)
    tabla.add_row("Producto", producto)
    tabla.add_row("Vigencia", f"{dias} días")
    tabla.add_row("Registros", str(total))

    console.print(
        Panel(
            tabla,
            title="[bold green]CONFIGURACIÓN[/bold green]",
            border_style="green",
        )
    )