from flask import Flask, request, jsonify
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# datos mock de simulacion
orders = {}
authorization_attempts = {}

# Endpoint  consultar el estado de un pedido
@app.route('/check_order_status', methods=['POST'])
def check_order_status():
    data = request.json
    user_code = data.get('user_code')
    order_code = data.get('order_code')

    if not user_code or not order_code:
        logger.error("Se requiere user_code y order_code")
        return jsonify({"error": "Se requiere user_code y order_code"}), 400

    return jsonify({"message": "Por favor ingrese su codigo OTP de autorización", "user_code": user_code}), 200

# Endpoint para verificar el código de autorización
@app.route('/verify_authorization', methods=['POST'])
def verify_authorization():
    data = request.json
    user_code = data.get('user_code')
    auth_code = data.get('auth_code')

    if not user_code or not auth_code:
        logger.error("Se requiere user_code, auth_code, y order_code")
        return jsonify({"error": "Se requiere user_code, auth_code, y order_code "}), 400

    # Inicializar el contador de intentos fallidos si no existe
    if user_code not in authorization_attempts:
        authorization_attempts[user_code] = 0

    # Simulación de un código de autorización válido
    valid_auth_code = "12345"

    if auth_code == valid_auth_code:
        authorization_attempts[user_code] = 0
        logger.info(f"Autorización exitosa para user_code: {user_code}")
        return jsonify({"message": "Authorization successful", "user_code": user_code}), 200
    else:
        # Incrementar el contador de intentos fallidos
        authorization_attempts[user_code] += 1

        if authorization_attempts[user_code] >= 2:
            trigger_alert(user_code)
            logger.warning(f"Intento de acceso no autorizado para user_code: {user_code}")
            return jsonify({"message": "Autorizacion fallida. enviando alerta", "user_code": user_code}), 403
        else:
            return jsonify({"message": "Autorizacion fallida, intenete de nuevo", "user_code": user_code}), 401


def trigger_alert(user_code):
    logger.info(f"ALERT: Unauthorized access attempt detected for user {user_code}")

    try:
        response = requests.post(
            'https://ccp-customer-order-not-6c19ecb88309.herokuapp.com/api/customer-order-notification',
            json={"user_code": user_code, "status": "RATE_LIMIT", "message": "Intento de acceso no autorizado detectado"},
            timeout=30
        )

        logger.info(f"Respuesta alerta status Code: {response.status_code} - Response Body: {response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send alert: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)