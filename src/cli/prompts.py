# src/cli/prompts.py

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt

from src.schemas.schemas import configuracion_envio

console = Console()


def pedir_archivo() -> str:
    console.print(
        Panel(
            "[bold cyan]Ingresa el nombre del archivo Excel[/bold cyan]\n\n"
            "[dim]Ejemplo: Helaboradores_sem_35[/dim]",
            title="[bold green]Configuración[/bold green]",
            border_style="green",
        )
    )

    while True:
        archivo = Prompt.ask(
            "Nombre del archivo",
            default="Helaboradores_sem_35",
        ).strip()

        if not archivo:
            console.print("[red]El nombre del archivo no puede estar vacío.[/red]")
            continue

        console.print(f"[green]Archivo configurado: {archivo}[/green]\n")

        return archivo


def pedir_fecha_vencimiento() -> str:
    console.print(
        Panel(
            "[bold cyan]Ingresa la fecha de vencimiento del cupón[/bold cyan]\n\n"
            "[dim]Ejemplo: 01/01/2026[/dim]",
            title="[bold green]Configuración[/bold green]",
            border_style="green",
        )
    )

    while True:
        fecha = Prompt.ask(
            "Fecha de vencimiento (fecha de caducidad del cupón)"
        ).strip()

        if not fecha:
            console.print("[red]La fecha de vencimiento no puede estar vacía.[/red]")
            continue

        console.print(f"[green]Vencimiento configurado: {fecha}[/green]\n")

        return fecha


def pedir_producto() -> str:
    console.print(
        Panel(
            "[bold cyan]Ingresa el producto del cupón[/bold cyan]\n\n"
            "[dim]Ejemplo: Doble Bolita[/dim]",
            title="[bold green]Configuración[/bold green]",
            border_style="green",
        )
    )

    while True:
        producto = Prompt.ask(
            "Producto",
            default="Doble Bolita",
        ).strip()

        if not producto:
            console.print("[red]El producto no puede estar vacío.[/red]")
            continue

        console.print(f"[green]Producto configurado: {producto}[/green]\n")

        return producto


def pedir_configuracion_envio() -> configuracion_envio:

    console.print(
        Panel(
            "[bold cyan]Configuración de envío[/bold cyan]\n\n"
            "Puedes utilizar la configuración recomendada o "
            "personalizar los tiempos de envío.",
            title="[bold green]Envíos[/bold green]",
            border_style="green",
        )
    )

    avanzada = Confirm.ask(
        "¿Deseas modificar la configuración avanzada?",
        default=False,
    )

    # Configuración recomendada
    if not avanzada:
        return configuracion_envio(
            tamano_lote=15,
            espera_mensaje=5,
            espera_lote=120,
        )

    console.print("\n[bold yellow]Configuración avanzada[/bold yellow]\n")

    tamano_lote = IntPrompt.ask(
        "Tamaño del lote",
        default=15,
    )

    espera_mensaje = IntPrompt.ask(
        "Espera entre correos (segundos)",
        default=5,
    )

    espera_lote = IntPrompt.ask(
        "Espera entre lotes (segundos)",
        default=120,
    )

    return configuracion_envio(
        tamano_lote=tamano_lote,
        espera_mensaje=espera_mensaje,
        espera_lote=espera_lote,
    )
