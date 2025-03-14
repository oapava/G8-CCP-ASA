from flask import Flask, request, jsonify
import os

orderIdStatus = {
    1: {"isBlock":False},
    2:{"isBlock":False}
}

app = Flask(__name__)

@app.route("/block", methods=["POST"])
def receive_message():
    data = request.get_json()
    if not data or "id" not in data:
        return jsonify({"error": "Message is required"}), 400
    messageID = int(data["id"])
    print("Received message:", messageID)
    orderIdStatus[messageID]["isBlock"] = True
    print(orderIdStatus)
    return jsonify({"success": True, "received": messageID})

@app.route('/<variable>')
def dynamic_route(variable):
    idNumber = int(variable)
    orderIdStatus[idNumber]["isBlock"] = False
    print(orderIdStatus)
    return f"Has desbloqueado la orden de entrega con ID: {variable}."

@app.route('/favicon.ico')
def favicon():
    return '', 204  # Responde con un código 204 (sin contenido)