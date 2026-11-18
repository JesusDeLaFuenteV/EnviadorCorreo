# EnviadorCorreo

API REST desarrollada con **Flask** y **SendGrid** para el envío de correos electrónicos mediante plantillas dinámicas. Incluye configuración para despliegue continuo en **Azure Web App** usando GitHub Actions.

## 🚀 Tecnologías utilizadas

- **Python 3.10**
- **Flask** – Framework web para exponer el endpoint REST
- **SendGrid** (`sendgrid`) – Cliente oficial para envío de correos con plantillas dinámicas
- **python-dotenv** – Carga de variables de entorno desde archivo `.env`
- **Gunicorn** – Servidor WSGI para producción

## 📁 Estructura del proyecto

```text
.
├── .github/
│   └── workflows/
│       └── main_apienviadorcorreo.yml  # Workflow de CI/CD para Azure Web App
├── .gitignore
├── requirements.txt                    # Dependencias del proyecto
├── send_email.py                       # Aplicación Flask y lógica de envío
└── start.sh                            # Script de inicio con Gunicorn
```

## ⚙️ Configuración local

1. **Clona el repositorio:**
   ```bash
   git clone <URL_DE_TU_REPOSITORIO>
   cd EnviadorCorreo
   ```

2. **Crea y activa un entorno virtual:**
   ```bash
   python -m venv venv
   # En Linux/macOS:
   source venv/bin/activate
   # En Windows:
   venv\Scripts\activate
   ```

3. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura las variables de entorno:**
   Crea un archivo `.env` en la raíz del proyecto (ignorado por Git según `.gitignore`) y agrega tu clave de API de SendGrid:
   ```env
   SENDGRID_API_KEY=tu_api_key_de_sendgrid
   ```

## ▶️ Ejecución

### Modo desarrollo (Flask)
```bash
python send_email.py
```
Por defecto se iniciará en `http://127.0.0.1:5000` en modo debug.

### Modo producción (Gunicorn)
El archivo `start.sh` ejecuta la aplicación con Gunicorn en el puerto `8000`:
```bash
gunicorn --bind=0.0.0.0:8000 --timeout 600 send_email:app
```

## 📬 Uso de la API

### `POST /api/send-email`

Envía un correo electrónico utilizando una plantilla dinámica de SendGrid.

#### Cuerpo de la solicitud (`application/json`)

Todos los siguientes campos son obligatorios:

| Campo | Tipo | Descripción |
| --- | --- | --- |
| `from` | `string` | Dirección de correo del remitente (verificada en SendGrid). |
| `to` | `string` | Dirección de correo del destinatario. |
| `template_id` | `string` | ID de la plantilla dinámica en SendGrid. |
| `dynamic_template_data` | `object` | Diccionario con las variables dinámicas de la plantilla. |

#### Ejemplo con `curl`

```bash
curl -X POST http://127.0.0.1:5000/api/send-email \
  -H "Content-Type: application/json" \
  -d '{
    "from": "remitente@tudominio.com",
    "to": "destinatario@ejemplo.com",
    "template_id": "d-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "dynamic_template_data": {
      "nombre": "Usuario",
      "mensaje": "Bienvenido a la plataforma"
    }
  }'
```

#### Respuestas

- **`202 Accepted`**: Correo enviado exitosamente.
  ```json
  {
    "message": "Correo enviado exitosamente",
    "response": {
      "status_code": 202,
      "body": null,
      "headers": {}
    }
  }
  ```
- **`400 Bad Request`**: Faltan campos requeridos (`from`, `to`, `template_id`, `dynamic_template_data`).
- **`500 Internal Server Error`**: Falta `SENDGRID_API_KEY`, la respuesta de SendGrid no fue `202` u ocurrió un error inesperado.

## ☁️ Despliegue en Azure

El repositorio incluye el workflow `.github/workflows/main_apienviadorcorreo.yml`, que construye y despliega automáticamente la aplicación en **Azure Web App** (`ApiEnviadorCorreo`, slot `Production`) al hacer `push` a la rama `main` o de forma manual mediante `workflow_dispatch`.

Para que funcione en tu repositorio de GitHub, asegúrate de tener configurados:
1. Los **Secrets** de autenticación de Azure en GitHub (`AZUREAPPSERVICE_CLIENTID_*`, `AZUREAPPSERVICE_TENANTID_*`, `AZUREAPPSERVICE_SUBSCRIPTIONID_*`).
2. La variable de entorno `SENDGRID_API_KEY` en la configuración (**Configuration / Environment variables**) de tu Azure Web App.
