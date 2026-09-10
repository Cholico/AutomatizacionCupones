# src/cli/menu.py

from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt
from rich.table import Table

console = Console()


def menu_principal() -> int:

    tabla = Table(
        show_header=False,
        box=None,
        padding=(0, 2),
    )

    tabla.add_column(style="bold cyan", justify="center")
    tabla.add_column(style="white")

    tabla.add_row("1", "Enviar cupones por correo")
    tabla.add_row("2", "Enviar cupones vía Twilio")
    tabla.add_row("3", "Consultar mensajes enviados de Twilio")
    tabla.add_row("4", "Consultar cupones pendientes en BD")
    tabla.add_row("0", "Salir")

    console.print(
        Panel(
            tabla,
            title="[bold green]MENÚ PRINCIPAL[/bold green]",
            subtitle="[dim]Selecciona una opción[/dim]",
            border_style="cyan",
        )
    )

    while True:
        opcion = IntPrompt.ask(
            "[bold cyan]Opción[/bold cyan]"
        )

        if opcion in [0, 1, 2, 3, 4]:
            return opcion

        console.print(
            "[red]Selecciona una opción válida entre 0 y 4.[/red]"
        )