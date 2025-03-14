from flask import Flask, jsonify, request


app = Flask(__name__)
USER = {
    "id": 126542,
    "name": "Omar Pava",
    "email": "o.pava@test.com",
    "adddress": [
        {
            "id": 1,
            "name": "address 1",
            "address": "calle 9 # 9 - 09",
            "city": "BOG",
            "country": "COL",
            "coordinates": {
                "lat":1332135,
                "lon":546543543654
            }
        }
    ]

}

@app.route('/api/customer-order-notification', methods=['POST'])
def get_alert():
    if not request.is_json:
        return jsonify({"error": "El cuerpo de la solicitud debe ser JSON"}), 400

    data = request.get_json()

    if "status" not in data or "message" not in data  or "user_code" not in data:
        return jsonify({"error": "Faltan los campos 'status', 'user code' o 'message'"}), 400
    
    respuesta_envio = send_alert_to_customer( data )

    return respuesta_envio


def send_alert_to_customer( data ):
    ##Consultar en la "BD" el usaurio
    if USER['id'] == data['user_code']: 
        send_alert = ""
        message_confirm = {
            "status": 200,
            "message": f"Se ha alertado al usuario {USER['id']} sobre el acceso a su cuenta"
        }
        return jsonify(message_confirm), 200 
    
    else:
        respuesta_fallida = {
            "status": 404,
            "message": "No se encontró el usuario"
        }
        return jsonify(respuesta_fallida), 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5006) 