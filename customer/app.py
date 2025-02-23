from flask import Flask, request, jsonify
import time, random


app = Flask(__name__)
timeOuts = [0,10,3]
choice = random.choice(timeOuts);

@app.route("/customers", methods=["POST"])
def add_customer():
    time.sleep(choice)
    customer = request.json
    
    if "name" not in customer or "registry" not in customer:
        return jsonify({"error": "Datos inválidos"}), 400
    
    return jsonify({
        "status": "Se agrego el nuevo cliente",
        "data": customer
    }), 200
    


