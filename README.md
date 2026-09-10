# 🚀 Automatización de Mensajería y Cupones (WhatsApp & Email)

<p align="left">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Twilio-F22F46?style=for-the-badge&logo=twilio&logoColor=white" alt="Twilio" />
  <img src="https://img.shields.io/badge/Microsoft%20Graph-0078D4?style=for-the-badge&logo=microsoft&logoColor=white" alt="Microsoft Graph" />
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
  <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub" />
  <img src="https://img.shields.io/badge/Rich-111111?style=for-the-badge&logo=python&logoColor=FF4500" alt="Rich" />
  <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas" />
  <img src="https://img.shields.io/badge/WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white" alt="WhatsApp" />
</p>

Sistema en Python para la automatización, generación y envío masivo de cupones personalizados. Permite la entrega multicanal mediante **WhatsApp (Twilio API)** y correos electrónicos **(Microsoft Graph API)**, almacena información persistente en **SQLite**, gestiona imágenes dinámicas en el CDN **RAW de GitHub**, ofrece una **CLI interactiva con Rich** y exporta reportes detallados en **Excel**.

## 💡 Contexto y Motivación

Como parte de los beneficios corporativos que otorga **Helados Dolphy**, la empresa emite cupones digitales dirigidos a dos públicos principales:
* **Empleados de la empresa:** Entrega personal e instantánea de beneficios e incentivos.
* **Empresas colaboradoras:** Distribución de cupones de descuento exclusivos para convenios corporativos vía correo electrónico.

### El Problema
Anteriormente, la distribución de estos cupones generaba cuellos de botella operativos y retrasos en las entregas.

### La Solución
Desde el área de **Sistemas**, desarrollamos este servicio integral para conectar todo el flujo de trabajo:
1. **Extracción y Generación:** Obtención de los códigos de cupones generados a través del módulo **Gift & Loyalty de Oracle**.
2. **Procesamiento de Archivos:** Generación automatizada de archivos de imagen y códigos QR únicos para cada cupón.
3. **Distribución Multicanal:**
   * **WhatsApp (Twilio API):** Envío directo al número de teléfono del colaborador.
   * **Email (Microsoft Graph API):** Envío formal a empresas y convenios colaboradores.
4. **Trazabilidad:** Registro persistente en **SQLite** y reportes consolidados en **Excel** para auditoría y seguimiento en tiempo real.

### 🎨 Inspiración de la Interfaz CLI
Dado que este sistema está destinado a ser utilizado por el equipo técnico de Sistemas, siempre existió la intención de ofrecer una consola estética y profesional. La inspiración para implementar **Rich** surgió de [este video de Linkfy](https://www.youtube.com/shorts/5cD59ttul1g), permitiendo transformar los procesos en la terminal en una experiencia interactiva con tablas formateadas, colores y barras de progreso en vivo.

---

## 🛠️ Tecnologías y Herramientas

| Componente | Tecnología | Descripción |
| :--- | :--- | :--- |
| **Lenguaje Base** | `Python 3.11+` | Lógica principal y empaquetado con PyInstaller (`.spec`). |
| **Interfaz CLI** | `Rich` | Interfaz gráfica por terminal, menús interactivos y barras de progreso. |
| **API WhatsApp** | `Twilio REST API` | Envío de plantillas interactivas (`Content Templates`). |
| **API Email** | `Microsoft Graph` | Integración con servicios de Microsoft 365 para envío alternativo de correos. |
| **Base de Datos** | `SQLite` | Almacenamiento local persistente para control de envíos y estado. |
| **CDN de Imágenes** | `GitHub API (RAW)` | Alojamiento dinámico de QR y cupones de alta disponibilidad. |
| **Gestión de Datos** | `Pandas` / `OpenPyXL` | Procesamiento de insumos y generación de reportes consolidados. |

---

## 📋 Funcionalidades Clave

* 🔀 **Envío Multicanal:** Soporte principal para WhatsApp y canal secundario/alternativo vía Microsoft Graph API para emails corporativos.
* 💾 **Persistencia con SQLite:** Registro local en base de datos para seguimiento histórico de cupones y control de duplicados.
* 🖥️ **CLI Avanzada (Rich):** Monitoreo con spinners de carga, barras de progreso y paneles formateados para una experiencia limpia en consola.
* 🖼️ **CDN sin Latencia:** Servido directo de imágenes y QRs desde `raw.githubusercontent.com` para evitar bloqueos por límites de tasa.
* 🛡️ **Sanitización de Datos:** Codificación automática de URLs (`urllib.parse.quote`) para evitar rechazos en las APIs por espacios o caracteres especiales.
* 📊 **Reportes e Historial:** Exportación de estados (`exito`, `sid`, `error_code`) en hojas de cálculo `.xlsx`.

---

## 🖼️ Galeria

<img width="1124" height="463" alt="Captura de pantalla 2026-09-10 112521" src="https://github.com/user-attachments/assets/32e8b067-0b5f-4edb-aaca-c4d81dc40e24" />

<img width="490" height="490" alt="0_Dolphyccino" src="https://github.com/user-attachments/assets/f90a1af5-04d0-4f8a-8dfb-fe416a1914f4" />


## 📂 Estructura del Proyecto

```text
AutomatizacionCupones/
│
├── data/                   # Archivos de base de datos SQLite
├── logs/                   # Historial de logs del sistema
├── qr_generados/           # Archivos de códigos QR generados localmente
├── reportes/               # Archivos Excel de salida (.xlsx)
│
├── src/
│   ├── assets/             # Recursos estáticos e imágenes del proyecto
│   ├── cli/                # Componentes y vistas de la interfaz con Rich
│   ├── consumidor/         # Hilos trabajadores (Workers) para procesar envíos
│   ├── core/               # Módulos principales y diccionarios del sistema y platillas
│   ├── database/           # Conexión, modelos y consultas SQLite
│   ├── graph/              # Cliente e integración con Microsoft Graph API
│   ├── schemas/            # Definición de datos y validaciones con Pydantic
│   ├── services/           # Lógica de negocio (generación de QR, cupones, etc.)
│   ├── twilio/             # Lógica y cliente para el envío de WhatsApp
│   ├── utils/              # Funciones auxiliares y herramientas
│   ├── config.py           # Variables globales de configuración
│   └── logger_config.py    # Configuración centralizada del sistema de logs
│
├── .env                    # Credenciales y variables de entorno
├── Envio Cupones.spec      # Script de compilación de PyInstaller
├── main.py                 # Punto de entrada de la aplicación
└── requirements.txt        # Dependencias del proyecto

---


Markdown

## 🚀 Guía de Instalación y Ejecución Local

Sigue estos pasos para clonar, configurar y ejecutar el proyecto en tu máquina local.

---

### 1. Requisitos Previos

Asegúrate de tener instalados los siguientes componentes antes de comenzar:

* **Git:** Para clonar el repositorio.
* **Python 3.11+:** Verificar versión ejecutando `python --version` en la terminal.

---

### 2. Clonar el Repositorio

Abre tu terminal o consola de comandos y ejecuta:

```bash
git clone [https://github.com/DolphyDev/cupones-whatsapp.git](https://github.com/DolphyDev/cupones-whatsapp.git)
cd cupones-whatsapp

3. Crear y Activar el Entorno Virtual

Es recomendable aislar las dependencias del proyecto utilizando venv:

    En Windows (CMD / PowerShell):
    DOS

    python -m venv .venv
    .venv\Scripts\activate

    En Linux / macOS:
    Bash

    python3 -m venv .venv
    source .venv/bin/activate

4. Instalar Dependencias

Con el entorno virtual activado, instala todas las librerías necesarias:
Bash

pip install --upgrade pip
pip install -r requirements.txt

5. Configurar Variables de Entorno

Crea un archivo llamado .env en la raíz del proyecto (junto a main.py) e incluye las credenciales correspondientes:
Fragmento de código

# Configuración de Twilio (WhatsApp)
ACCOUNT_SID=tu_account_sid_aqui
AUTH_TOKEN=tu_auth_token_aqui
TEMPLATE_SID=tu_content_sid_de_plantilla

# Configuración de Microsoft Graph API (Email)
GRAPH_CLIENT_ID=tu_client_id_aqui
GRAPH_TENANT_ID=tu_tenant_id_aqui
GRAPH_CLIENT_SECRET=tu_client_secret_aqui

6. Ejecutar la Aplicación

Una vez configuradas las variables de entorno, inicia el servicio mediante la interfaz interactiva de CLI:
Bash

python main.py

    Nota: Al ejecutar main.py, el script creará automáticamente la estructura de directorios necesaria (data/, logs/, qr_generados/ y reportes/) si aún no existen en tu entorno local.
```
**P.D.** Hay planes para refactorizar la lógica de mensajes y dar mayor flexibilidad a la gestión dinámica de plantillas; sin embargo, el desarrollo se encuentra pausado temporalmente debido a otros proyectos prioritarios en **Helados Dolphy**.
