import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
from flask import Flask, request, jsonify

load_dotenv()

app = Flask(__name__)
def send_email_with_sendgrid(
    from_email: str,
    to_emails: str,
    template_id: str,
    dynamic_template_data: dict
) -> dict:
    """
    Envía un correo electrónico usando la Web API de SendGrid y una plantilla.
    
    Args:
        from_email: La dirección de correo del remitente.
        to_emails: La dirección de correo del destinatario.
        template_id: El ID de la plantilla de SendGrid a utilizar.
        dynamic_template_data: Un diccionario de datos para la plantilla.
    
    Returns:
        Un diccionario con el estado de la respuesta de SendGrid.
    """
    # Obtiene la clave de API desde las variables de entorno
    sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')
    
    if not sendgrid_api_key:
        raise ValueError("SENDGRID_API_KEY no encontrada en las variables de entorno.")
    # Crea el objeto de mensaje
    message = Mail(
        from_email=from_email,
        to_emails=to_emails
    )
    
    # Asigna el ID de la plantilla y los datos dinámicos
    message.template_id = template_id
    message.dynamic_template_data = dynamic_template_data
    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        
        # --- CORRECCIÓN AQUÍ ---
        # Decodifica response.body de bytes a string antes de devolverlo
        body_content = response.body.decode('utf-8') if response.body else None
        
        # Convierte los headers a un diccionario que sea serializable
        headers_dict = dict(response.headers)
        
        return {
            "status_code": response.status_code,
            "body": body_content,
            "headers": headers_dict
        }
    except Exception as e:
        raise e
# Endpoint de la API para enviar correos
@app.route('/api/send-email', methods=['POST'])
def send_email_endpoint():
    """
    Endpoint que recibe los datos de un correo por JSON y lo envía.
    """
    # Obtiene los datos de la solicitud POST en formato JSON
    data = request.get_json()
    # Valida que los datos necesarios estén presentes
    if not all(k in data for k in ['from', 'to', 'template_id', 'dynamic_template_data']):
        return jsonify({"error": "Faltan campos requeridos: 'from', 'to', 'template_id', 'dynamic_template_data'"}), 400
    sender = data['from']
    recipient = data['to']
    template_id = data['template_id']
    dynamic_template_data = data['dynamic_template_data']
    try:
        # Llama a la función que envía el correo
        response_data = send_email_with_sendgrid(
            from_email=sender,
            to_emails=recipient,
            template_id=template_id,
            dynamic_template_data=dynamic_template_data
        )
        # Si el envío fue exitoso, devuelve una respuesta JSON
        if response_data.get("status_code") == 202:
            return jsonify({"message": "Correo enviado exitosamente", "response": response_data}), 202
        else:
            return jsonify({"error": "El envío de correo falló", "response": response_data}), 500
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 500
    except Exception as e:
        return jsonify({"error": f"Ocurrió un error inesperado: {str(e)}"}), 500
if __name__ == '__main__':
    # Ejecuta la aplicación en modo de depuración
    # En producción, usar un servidor como Gunicorn o Waitress
    app.run(debug=True)