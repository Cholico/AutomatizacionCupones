import base64
import time
from pathlib import Path

import requests

from src.config import settings


class ErrorSubidaImagen(Exception):
    pass


def upload_to_github(ruta_qr: Path) -> str:
    
    # 1. Datos de configuración
    repo_owner = settings.GITHUB_USER
    repo_name = settings.GITHUB_REPO
    token = settings.GITHUB_TOKEN
    
    # Nombre del archivo remoto (se guarda en una carpeta dentro del repo)
    filename = ruta_qr.name
    path_in_repo = f"cupones_{settings.FECHA_ACTUAL.isocalendar().week}_{settings.FECHA_ACTUAL.year}/{filename}"
    branch = "main"

    # Endpoint oficial de GitHub API para contenidos
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{path_in_repo}"

    # 2. Leer la imagen local y convertirla a Base64
    try:
        with open(ruta_qr, "rb") as file:
            content_b64 = base64.b64encode(file.read()).decode("utf-8")
    except Exception as e:
        raise ErrorSubidaImagen(f"No se pudo leer el archivo local: {e}")

    # 3. Encabezados y cuerpo de la petición
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    payload = {
        "message": f"upload QR: {filename}",
        "content": content_b64,
        "branch": branch,
    }

    # 4. Enviar la petición PUT
    try:
        # Pausa ligera preventiva entre peticiones
        time.sleep(2)

        res = requests.put(url, json=payload, headers=headers)

        if res.status_code in [200, 201]:
            # Manda la imagen a github
            return f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{branch}/{path_in_repo}"
        else:
            print("Error GitHub API:", res.text)
            raise ErrorSubidaImagen(f"Error al subir imagen a GitHub ({res.status_code}): {res.text}")

    except (requests.exceptions.RequestException, Exception) as e:
        raise ErrorSubidaImagen(f"Error de conexión con GitHub API: {e}")