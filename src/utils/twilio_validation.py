from rich.console import Console
from rich.panel import Panel
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from src.config import settings

console = Console()


class TwilioValidationError(Exception):
    pass



def validar_cuenta_twilio(credito_minimo: float = 1.0) -> bool:
    """
    Valida las credenciales de Twilio y verifica si hay crédito disponible.
    
    :param credito_minimo: Saldo mínimo requerido para permitir el flujo (ej. 1.0 USD/MXN).
    :return: True si todo está en orden, False si fallan las credenciales o el saldo.
    """
    try:
        client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)

        # 1. Validar Credenciales consultando los datos de la cuenta
        account = client.api.v2010.account.fetch()

        if account.status != "active":
            console.print(
                Panel(
                    f"[bold red]❌ LA CUENTA DE TWILIO NO ESTÁ ACTIVA[/bold red]\n\n"
                    f"[white]Estado actual: {account.status}[/white]",
                    border_style="red",
                    padding=(1, 2),
                )
            )
            return False

        # 2. Consultar Saldo/Crédito Disponible
        balance_data = client.balance.fetch()
        saldo_actual = float(balance_data.balance)
        moneda = balance_data.currency

        if saldo_actual < credito_minimo:
            console.print(
                Panel(
                    f"[bold red]⚠️ CRÉDITO INSUFICIENTE EN TWILIO[/bold red]\n\n"
                    f"📊 [white]Saldo disponible:[/white] [yellow]{saldo_actual:.2f} {moneda}[/yellow]\n"
                    f"🎯 [white]Mínimo requerido:[/white] {credito_minimo:.2f} {moneda}\n\n"
                    f"[white]Recarga tu cuenta de Twilio antes de continuar.[/white]",
                    border_style="red",
                    padding=(1, 2),
                )
            )
            return False

        return True

    except TwilioRestException as e:
        # Error 20003 suele ser de Autenticación (Account SID / Auth Token incorrectos)
        console.print(
            Panel(
                f"[bold red]❌ ERROR DE CREDENCIALES DE TWILIO[/bold red]\n\n"
                f"Código de error: [yellow]{e.code}[/yellow]\n"
                f"Detalle: [white]{e.msg}[/white]\n\n"
                f"[dim]Verifica ACCOUNT_SID y AUTH_TOKEN en tu archivo .env[/dim]",
                border_style="red",
                padding=(1, 2),
            )
        )
        return False
    except TwilioValidationError as e:
        console.print(f"[red]❌ Error de validación de Twilio: {e}[/red]")
        return False