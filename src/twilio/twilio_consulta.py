import pandas as pd
from rich.console import Console
from rich.progress import track
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from src.config import settings

console = Console()


def verificar_estatus_real_twilio(df_mensajes: pd.DataFrame) -> pd.DataFrame:

    # Normalizar nombre de la columna SID
    col_sid = "sid" if "sid" in df_mensajes.columns else "SID"

    client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
    registros_no_entregados = []

    console.print(
        "\n[bold cyan]🔍 Verificando estados en tiempo real con la API de Twilio...[/bold cyan]"
    )

    for idx, row in track(
        df_mensajes.iterrows(),
        total=len(df_mensajes),
        description="Consultando Twilio...",
    ):
        sid = row.get(col_sid)
        row_dict = row.to_dict()

        # Si no llegó a tener SID (falló antes de la llamada a la API)
        if not sid or pd.isna(sid):
            row_dict["Estatus API"] = "sin_sid"
            row_dict["Detalle Error API"] = (
                row_dict.get("motivo")
                or row_dict.get("Detalle Error")
                or "Error previo a Twilio"
            )
            registros_no_entregados.append(row_dict)
            continue

        try:
            # Consulta directa a la API de Twilio mediante el SID
            message = client.messages(sid).fetch()
            estatus_api = (
                message.status
            )  # 'delivered', 'read', 'failed', 'undelivered', 'queued', etc.

            # Si el mensaje NO fue entregado ni leído
            if estatus_api not in ["delivered", "read"]:
                row_dict["Estatus API"] = estatus_api
                row_dict["Codigo Error API"] = message.error_code or "N/A"
                row_dict["Detalle Error API"] = (
                    message.error_message or "Mensaje no entregado"
                )
                registros_no_entregados.append(row_dict)

        except TwilioRestException as e:
            row_dict["Estatus API"] = "error_api"
            row_dict["Detalle Error API"] = f"Error al consultar SID: {e.msg}"
            registros_no_entregados.append(row_dict)

    df_resultado = pd.DataFrame(registros_no_entregados)
    return df_resultado
