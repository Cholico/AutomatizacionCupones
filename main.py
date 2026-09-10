import ctypes
import sys

from rich.console import Console

from src.cli.menu import menu_principal
from src.database.connection import inicializar_bd
from src.logger_config import configurar_logging
from src.services.consultar_envios import consultar_envios
from src.services.consultar_twilio import consultar_twilio
from src.services.envio_cupones import envio_cupones
from src.utils.limpiar_pantalla import limpiar_pantalla
from src.utils.red import validar_red_antes_de_enviar
from src.utils.twilio_validation import validar_cuenta_twilio

configurar_logging()

console = Console()

def establecer_icono_ventana():
    """Asigna el icono a la ventana de la consola en Windows."""
    if sys.platform == "win32":
        from src.config import settings
        ruta_icono = settings.BASE_DIR / "src" / "assets" / "img" / "dolphy_logo.ico"
        if ruta_icono.exists():
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            if hwnd:
                hicon = ctypes.windll.user32.LoadImageW(
                    None,
                    str(ruta_icono),
                    1,  # IMAGE_ICON
                    0, 0,
                    0x00000010 | 0x00000020  # LR_LOADFROMFILE | LR_DEFAULTSIZE
                )
                ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 0, hicon)
                ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 1, hicon)


def main():
    establecer_icono_ventana()
    inicializar_bd()  # Asegurarse de que la BD y las tablas existan

    try:
        while True:
            limpiar_pantalla()
            opcion = menu_principal()

            match opcion:
                case 1:
                    # Enviar cupones por correo (requiere red)
                    if validar_red_antes_de_enviar():
                        envio_cupones(tipo_envio="correo")
                    else:
                        input("\nPresiona ENTER para volver al menú...")

                case 2:
                    # Enviar cupones por Twilio (requiere red)
                    if validar_red_antes_de_enviar() and validar_cuenta_twilio():
                        envio_cupones(tipo_envio="twilio")
                    else:
                        input("\nPresiona ENTER para volver al menú...")

                case 3:
                    # Consultar API de Twilio (requiere red)
                    if validar_red_antes_de_enviar() and validar_cuenta_twilio():
                        consultar_twilio()
                    else:
                        input("\nPresiona ENTER para volver al menú...")

                case 4:
                    # Consultar BD local (funciona con o sin red)
                    consultar_envios()

                case 0:
                    return
                
    except KeyboardInterrupt:
        console.print("\n\n[yellow]👋 Aplicación cerrada por el usuario.[/yellow]\n")
        sys.exit(0)


if __name__ == "__main__":
    main()