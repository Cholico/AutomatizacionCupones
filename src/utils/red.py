import socket

from rich.console import Console
from rich.panel import Panel

console = Console()


def hay_conexion_internet(host="8.8.8.8", puerto=53, timeout=3) -> bool:
    try:
        socket.setdefaulttimeout(timeout)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, puerto))
        return True
    except (socket.OSError, OSError):
        return False


def validar_red_antes_de_enviar():
    if not hay_conexion_internet():
        console.print(
            Panel(
                "[bold red]❌ ERROR DE CONEXIÓN[/bold red]\n\n"
                "[white]No se detecta acceso a internet. Revisa tu red antes de continuar.[/white]",
                border_style="red",
                padding=(1, 2)
            )
        )
        return False
    return True

