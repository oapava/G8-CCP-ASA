import os
import json
import time
import pika
import threading
from collections import defaultdict
from flask import Flask, jsonify

app = Flask(__name__)

CLOUDAMQP_URL = os.environ.get(
    'CLOUDAMQP_URL', 'amqps://wvvfljaz:w9AfQi2yFo_obuplLkkV8HjKNrt7GA3M@moose.rmq.cloudamqp.com/wvvfljaz')

params = pika.URLParameters(CLOUDAMQP_URL)
TIMEOUT = 1
voting = defaultdict(list)

def callback(ch, method, properties, body):
    """ Función de callback para procesar mensajes de RabbitMQ """
    final_route = json.loads(body.decode()) 
    idRoute = final_route[0].get("idRoute", None) if final_route else None
    
    voting[idRoute].append(final_route) 
    if len(voting[idRoute]) == 1:
        threading.Thread(target=validate_vote, args=(idRoute,), daemon=True).start()

    ch.basic_ack(delivery_tag=method.delivery_tag)

def validate_vote(idRoute):
    """ Valida si se han recibido suficientes votos """
    start_time = time.time()
    
    while True:
        if len(voting[idRoute]) >= 3:
            print(f"✅ Recibidos 3 votos para {idRoute}: {voting[idRoute][0][0]}")
            validateUnique(voting[idRoute][0][0], voting[idRoute][1][0], voting[idRoute][2][0])
            del voting[idRoute]
            break
        
        if time.time() - start_time > TIMEOUT:
            print(f"❌ No llegaron 3 votos para {idRoute} en {TIMEOUT} segundo(s). Se recibieron solo {len(voting[idRoute])} voto(s)")
            del voting[idRoute] 
            break

        time.sleep(0.5)

def validateUnique(route1, route2, route3):
    unique_objs = {tuple(obj.items()) for obj in [route1, route2, route3]}
    if len(unique_objs) == 1:
        print("✅ Los 3 objetos son exactamente iguales")
    elif len(unique_objs) == 2:
        print("⚠️ Hay 2 objetos iguales y 1 diferente")
    else:
        print("❌ Los 3 objetos son diferentes")

def start_consumer():
    """ Inicia el consumidor en un hilo separado """
    consumer_connection = pika.BlockingConnection(params)
    consumer_channel = consumer_connection.channel()

    consumer_channel.queue_declare(queue='routes_voting', durable=True)
    consumer_channel.basic_consume(queue='routes_voting', on_message_callback=callback, auto_ack=False)

    print("🔄 Esperando mensajes...")
    consumer_channel.start_consuming()

# Ejecutar el consumidor en un hilo aparte
threading.Thread(target=start_consumer, daemon=True).start()

@app.route("/")
def health_check():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    print("🚀 Servicio Flask iniciado en Cloud Run...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=True)
