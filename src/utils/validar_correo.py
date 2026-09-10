import re

REGEXP_CORREO = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

def es_correo_valido(correo: str) -> bool:
    return bool(REGEXP_CORREO.match(correo))