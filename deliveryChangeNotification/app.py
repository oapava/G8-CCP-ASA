from flask import Flask, request, jsonify
import os
import smtplib

email_user = os.environ['email_user']
email_password = os.environ['email_password']
emails_clients = [
    {"id": 1, "correo": "p.riverah@uniandes.edu.co"},
    {"id": 2, "correo": "privera05@hotmail.com"}
]


app = Flask(__name__)

@app.route("/notify", methods=["POST"])
def receive_message():
    data = request.get_json()
    if not data or "id" not in data:
        return jsonify({"error": "Message is required"}), 400
    
    messageID = int(data["id"])
    print("Received message:", messageID)
    email_receiver = next((item['correo'] for item in emails_clients if item['id'] == messageID ),None)
    print(email_receiver)
    emailSend(email_user,email_password,email_receiver, messageID)
    return jsonify({"success": True, "received": messageID})

def emailSend(userEmail,password, email_receiver, messageID):
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        link = f"https://blockdelivery-7bbb91161050.herokuapp.com/{messageID}"
        bodyMsg = f"La direccion de entrega de la orden con ID {messageID} ha sido modificada.\nPara confirmar esta accion visite el siguiente link: {link}"
        msg = f'Subject: Bloqueo de orden {messageID}\n\n{bodyMsg}'

        smtp.login(userEmail,password)

        smtp.sendmail(userEmail,email_receiver,msg)
