from flask import Flask, jsonify
import os
import pika
import json
import threading  
import random

app = Flask(__name__)

CLOUDAMQP_URL = os.environ.get(
    'CLOUDAMQP_URL', 'amqps://wvvfljaz:w9AfQi2yFo_obuplLkkV8HjKNrt7GA3M@moose.rmq.cloudamqp.com/wvvfljaz')

params = pika.URLParameters(CLOUDAMQP_URL)

ROUTES = [
    {"id": 1, "origin": "Bogotá", "destination": "Medellín", "distance_km": 416, "estimated_time_hours": 8, "status": "active"},
    {"id": 2, "origin": "Medellín", "destination": "Cali", "distance_km": 420, "estimated_time_hours": 9, "status": "inactive"},
    {"id": 3, "origin": "Cali", "destination": "Cartagena", "distance_km": 1000, "estimated_time_hours": 18, "status": "active"},
    {"id": 4, "origin": "Bogotá", "destination": "Barranquilla", "distance_km": 994, "estimated_time_hours": 16, "status": "pending"}
]

def callback(ch, method, properties, body):
    """ Función que se ejecuta al recibir un mensaje en la cola dinámica de cada consumidor. """
    try:
        requestedRoute = json.loads(body.decode())
        print(f"📩 [Evento Recibido] {requestedRoute}")
        selectRoute(requestedRoute)
        ch.basic_ack(delivery_tag=method.delivery_tag) 
    except json.JSONDecodeError as e:
        print(f"❌ Error al decodificar JSON: {e}")

def selectRoute(route):
    """ Busca si la ruta existe y la envía a RabbitMQ si es válida. """
    destination_filter = route['destination']
    filtered_routes = list(filter(lambda r: r["destination"] == destination_filter, ROUTES))
    filtered_routes[0]['idRoute'] = route['idRoute']

    random_value = random.choice([ filtered_routes, [{'id': 3, 'origin': '', 'destination': '', 'distance_km': 1000, 'estimated_time_hours': 18, 'status': '','idRoute': route['idRoute']}] ])

    if filtered_routes:
        sendMessageToRoutesVotingQueue( random_value )
    else:
        print(f"❌ No se encontró ninguna ruta con destino '{route['destination']}'")

def sendMessageToRoutesVotingQueue(vote):
    """ Envía un mensaje a la cola 'routes_voting' en RabbitMQ. """
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue='routes_voting', durable=True)

    channel.basic_publish(
        exchange='',
        routing_key='routes_voting',
        body=json.dumps(vote), 
        properties=pika.BasicProperties(delivery_mode=2)
    )
    print(f"✅ Mensaje enviado a 'routes_voting': {vote}")

    connection.close()

def start_consumer():
    """ Configura el consumidor para escuchar eventos del Exchange 'routes_exchange'. """
    consumer_connection = pika.BlockingConnection(params)
    consumer_channel = consumer_connection.channel()

    consumer_channel.exchange_declare(exchange='routes_exchange', exchange_type='fanout')

    result = consumer_channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    consumer_channel.queue_bind(exchange='routes_exchange', queue=queue_name)

    print(f"🔄 [Consumidor Activo] Escuchando en {queue_name}...")

    consumer_channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=False)
    consumer_channel.start_consuming()

threading.Thread(target=start_consumer, daemon=True).start()

if __name__ == '__main__':
    print("🚀 Servicio Flask iniciado en puerto 5001...")
    app.run(port=5002, debug=True)
