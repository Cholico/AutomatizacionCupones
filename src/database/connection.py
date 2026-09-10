import sqlite3

from src.config import settings

# Ruta a la base de datos centralizada
DB_PATH = settings.BASE_DIR / "data" / "registro_cupones.db"


def obtener_conexion() -> sqlite3.Connection:
    """Devuelve una conexión a la BD SQLite con PRAGMA WAL activado para mejor rendimiento."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = (
        sqlite3.Row
    )  # Permite acceder a las columnas por nombre como diccionario
    return conn


def inicializar_bd() -> None:
    """Crea las tablas de envíos (Twilio y Correo) junto con sus índices para filtrado rápido."""
    with obtener_conexion() as conn:
        cursor = conn.cursor()

        # Activar el modo WAL para escrituras y lecturas concurrentes sin bloqueos
        cursor.execute("PRAGMA journal_mode=WAL;")

        # Tabla para envíos de WhatsApp via Twilio
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS envios_twilio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_emp TEXT NOT NULL,
                codigo TEXT NOT NULL,
                nombre TEXT NOT NULL,
                tienda TEXT NOT NULL,
                telefono TEXT NOT NULL,
                producto TEXT NOT NULL,
                fecha_vencimiento TEXT NOT NULL,
                semana INTEGER NOT NULL,
                estatus TEXT NOT NULL,
                sid TEXT,
                motivo TEXT,
                fecha_registro TEXT DEFAULT (datetime('now', 'localtime'))
            )
            """
        )

        # Tabla para envíos de Correo via Graph API
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS envios_correo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_emp TEXT NOT NULL,
                codigo TEXT NOT NULL,
                nombre TEXT NOT NULL,
                tienda TEXT NOT NULL,
                correo TEXT NOT NULL,
                producto TEXT NOT NULL,
                fecha_vencimiento TEXT NOT NULL,
                semana INTEGER NOT NULL,
                estatus TEXT NOT NULL,
                motivo TEXT,
                fecha_registro TEXT DEFAULT (datetime('now', 'localtime'))
            )
            """
        )

        # Índices estratégicos para acelerar consultas por semana, estatus, código y SID
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_twilio_semana_estatus ON envios_twilio(semana, estatus);"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_twilio_codigo ON envios_twilio(codigo);"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_twilio_sid ON envios_twilio(sid);"
        )

        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_correo_semana_estatus ON envios_correo(semana, estatus);"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_correo_codigo ON envios_correo(codigo);"
        )

        conn.commit()

