import pika
import os
import json
import time
import threading
import logging
import sys

# Configurar logging para Cloud Run
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(threadName)s] %(levelname)s: %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)]
)

CLOUDAMQP_URL = os.environ.get(
    'CLOUDAMQP_URL',
    'amqps://wvvfljaz:w9AfQi2yFo_obuplLkkV8HjKNrt7GA3M@moose.rmq.cloudamqp.com/wvvfljaz'
)

# Diccionario para monitorear heartbeats
hearthbeat = {
    1: {"time": 0},
    2: {"time": 0},
    3: {"time": 0}
}


def callback(ch, method, properties, body):
    """ Maneja los mensajes recibidos de RabbitMQ """
    resultado = json.loads(body.decode())
    if resultado["status"] == 200:
        hearthbeat[resultado["id"]]["time"] = 0
    logging.info(f"✅ Recibido heartbeat del componente #{resultado['id']} con estado {resultado['status']}")
    logging.info(f"📊 Estado actual: {hearthbeat}")


def log_status():
    """ Monitorea los heartbeats y registra en logs si un componente está inactivo """
    while True:
        time.sleep(30)
        for x in range(1, 4):
            hearthbeat[x]['time'] += 30
        logging.info("🔄 Revisión cada 30 segundos")
        logging.info(f"📊 Estado actual: {hearthbeat}")
        for x in range(1, 4):
            if hearthbeat[x]["time"] >= 60:
                logging.critical(f"⚠️ Componente {x} INACTIVO desde hace {hearthbeat[x]['time']} segundos")


def start_rabbitmq_consumer():
    """ Mantiene la conexión a RabbitMQ y reintenta en caso de fallo """
    while True:
        try:
            params = pika.URLParameters(CLOUDAMQP_URL)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            channel.queue_declare(queue='routes_voting_heartbeat', durable=True)
            channel.basic_consume(
                queue='routes_voting_heartbeat',
                on_message_callback=callback,
                auto_ack=True
            )
            logging.info("📡 Escuchando mensajes de RabbitMQ...")
            channel.start_consuming()
        except Exception as e:
            logging.error(f"⚠️ Error en RabbitMQ: {e}. Reintentando en 5 segundos...")
            time.sleep(5)  # Esperar antes de reintentar


def main(request):
    # 🧵 Hilo para monitorear heartbeats
    status_thread = threading.Thread(target=log_status, daemon=True, name="Monitor-Heartbeats")
    status_thread.start()

    # 🧵 Hilo para consumir mensajes de RabbitMQ con reconexión automática
    consumer_thread = threading.Thread(target=start_rabbitmq_consumer, daemon=True, name="RabbitMQ-Consumer")
    consumer_thread.start()

    # 🔄 Mantener el servicio en ejecución
    while True:
        time.sleep(3600)

    return {"status": "Se recibio el mensaje"}