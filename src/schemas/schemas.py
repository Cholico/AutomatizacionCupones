from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class configuracion_envio(BaseModel):
    tamano_lote: int
    espera_mensaje: int
    espera_lote: int


class payload_cupon(BaseModel):
    id_emp: str
    qr_path: Path
    nombre: str
    telefono: str
    correo: str
    codigo: str
    tienda: str
    producto: str
    fecha_vencimiento: str


class GraphAccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    ext_expires_in: int | None = None
    # Permite mapear campos extra si MSAL los envía sin lanzar error
    model_config = {"extra": "ignore"}


class MensajeBase(BaseModel):
    id_emp: str
    codigo: str
    nombre: str
    tienda: str
    producto: str
    fecha_vencimiento: str
    semana: int
    fecha_registro: datetime = Field(default_factory=datetime.now)


class MensajeTwilio(MensajeBase):
    telefono: str
    estatus: Literal[
        "queued", "sent", "delivered", "read", "failed", "undelivered", "error"
    ]
    sid: str | None = None
    motivo: str | None = None


class MensajeCorreo(MensajeBase):
    correo: str
    estatus: Literal["sent", "failed", "error"]
    motivo: str | None = None


class RespuestaTwilio(BaseModel):
    exito: bool
    sid: str | None = None
    status: str
    error_code: int | None = None
    error_message: str | None = None
