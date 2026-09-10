import re


def es_telefono_valido(telefono: str) -> bool:
    """Valida si un string contiene exactamente 10 dígitos numéricos."""
    if not telefono:
        return False
    # Limpia espacios, guiones o paréntesis en caso de que vengan formateados
    limpio = re.sub(r"\D", "", str(telefono))
    return len(limpio) == 10
