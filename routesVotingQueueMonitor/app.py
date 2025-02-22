import pika
import os
import json
import time
import threading
import logging

log_filename = "componentsFail.log"

if os.path.exists(log_filename):
    with open(log_filename) as log_file:
        pass

logging.basicConfig(
    filename=log_filename,
    level=logging.CRITICAL,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S"
    )

CLOUDAMQP_URL = os.environ.get(
    'CLOUDAMQP_URL', 'amqps://wvvfljaz:w9AfQi2yFo_obuplLkkV8HjKNrt7GA3M@moose.rmq.cloudamqp.com/wvvfljaz')

params = pika.URLParameters(CLOUDAMQP_URL)
connection = pika.BlockingConnection(params)
channel = connection.channel()
hearthbeat = {
    1:{"time":0},
    2:{"time":0},
    3:{"time":0}
}

channel.queue_declare(queue='routes_voting_heartbeat', durable=True)

def callback(ch, method, properties, body):
    resultado = json.loads(body.decode())
    if resultado["status"] == 200:
        hearthbeat[resultado["id"]]["time"] = 0
    print(f"Se recibio hearthbeat del componente de rutas #{resultado['id']}, con estado {resultado['status']}")
    print(hearthbeat)

channel.basic_consume(
    queue='routes_voting_heartbeat',
    on_message_callback=callback,
    auto_ack=True
)

def log_status():
    while True:
        time.sleep(30)
        hearthbeat[1]['time'] += 30
        hearthbeat[2]['time'] += 30
        hearthbeat[3]['time'] += 30
        print("Mensaje cada 30 segundos")
        print(hearthbeat)
        for x in range(1,4):
            if hearthbeat[x]["time"] >= 60:
                logging.critical(f"El componente {x} esta inactivo, desde hace {hearthbeat[x]['time']} segundos no manda señale de vida")



status_thread = threading.Thread(target=log_status, daemon=True)
status_thread.start()

print("Esperando mensajes")
channel.start_consuming()