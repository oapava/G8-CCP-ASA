from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/deliveryAddress/change", methods=["GET"])
def change_delivery_address():
    order_id=request.args.get('orderId', default=None)
    new_address=request.args.get('newAddress', default=None)

    if order_id == None:
        return "Debe especificar el Id de la orden.", 400
    
    if new_address == None:
        return "Debe especificar la nueva dirección.", 400

    try:
        send_post("https://blockdelivery-7bbb91161050.herokuapp.com/block",order_id)      #Block
        send_post("https://notificationdelivery-4b33d55135e0.herokuapp.com/notify",order_id)   #Notify
        return "Por seguridad, el despacho ha sido bloqueado hasta confirmar la nueva dirección."
    except Exception as e:
        return "Error, por favor vuelva a intentarlo.", 500

def send_post(url,order_id):
    response = requests.post(
        url,
        json={"id": order_id},
        headers={
            "Content-Type": "application/json" 
        },
        timeout=5
    )

    status_code = response.status_code

    if status_code not in (200,201):
        raise Exception(f"Error: {status_code} {response.text}")