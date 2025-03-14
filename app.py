import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Datos mock de simulación
orders = {}
authorization_attempts = {}

# Endpoint para consultar el estado de un pedido
@app.route('/check_order_status', methods=['POST'])
def check_order_status():
    data = request.json
    user_code = data.get('user_code')
    order_code = data.get('order_code')

    if not user_code or not order_code:
        print("Se requiere user_code y order_code")
        return jsonify({"error": "Se requiere user_code y order_code"}), 400

    return jsonify({"message": "Por favor ingrese su código de autorización", "user_code": user_code}), 200

# Endpoint para verificar el código de autorización
@app.route('/verify_authorization', methods=['POST'])
def verify_authorization():
    data = request.json
    user_code = data.get('user_code')
    auth_code = data.get('auth_code')

    if not user_code or not auth_code:
        print("Se requiere user_code y auth_code")
        return jsonify({"error": "Se requiere user_code y auth_code"}), 400

    # Inicializar el contador de intentos fallidos si no existe
    if user_code not in authorization_attempts:
        authorization_attempts[user_code] = 0

    # Simulación de un código de autorización válido
    valid_auth_code = "12345"

    if auth_code == valid_auth_code:
        authorization_attempts[user_code] = 0
        return jsonify({"message": "Autorización exitosa", "user_code": user_code}), 200
    else:
        # Incrementar el contador de intentos fallidos
        authorization_attempts[user_code] += 1

        if authorization_attempts[user_code] >= 2:
            trigger_alert(user_code)
            return jsonify({"message": "Autorización fallida. Enviando alerta", "user_code": user_code}), 403
        else:
            return jsonify({"message": "Autorización fallida, intente de nuevo", "user_code": user_code}), 401

def trigger_alert(user_code):
    print(f"ALERT: Intento de acceso no autorizado para el usuario {user_code}")

    try:
        response = requests.post(
            'https://ccp-customer-order-not-6c19ecb88309.herokuapp.com/api/customer-order-notification',
            json={"user_code": user_code, "status": "RATE_LIMIT", "message": "Intento de acceso no autorizado detectado"},
            timeout=10
        )
        print(f"Respuesta de alerta - Status Code: {response.status_code} - Response Body: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar la alerta: {e}")

if __name__ == '__main__':
    # Heroku asigna automáticamente el puerto, lo obtenemos de las variables de entorno
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
