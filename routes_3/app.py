from flask import Flask, jsonify
import random
import os
import pika
import json

app = Flask(__name__)

# URL COLA DE MENSAJERÍA
url = os.environ.get('CLOUDAMQP_URL',
                     'amqps://wvvfljaz:w9AfQi2yFo_obuplLkkV8HjKNrt7GA3M@moose.rmq.cloudamqp.com/wvvfljaz')


@app.route('/route')
def route():
    routes = [
        {
            "id": 1,
            "origin": "Bogotá",
            "destination": "Medellín",
            "distance_km": 416,
            "estimated_time_hours": 8,
            "status": "active"
        },
        {
            "id": 2,
            "origin": "Medellín",
            "destination": "Cali",
            "distance_km": 420,
            "estimated_time_hours": 9,
            "status": "inactive"
        },
        {
            "id": 3,
            "origin": "Cali",
            "destination": "Cartagena",
            "distance_km": 1000,
            "estimated_time_hours": 18,
            "status": "active"
        },
        {
            "id": 4,
            "origin": "Bogotá",
            "destination": "Barranquilla",
            "distance_km": 994,
            "estimated_time_hours": 16,
            "status": "pending"
        }
    ]

    ##respuesta_aleatoria = random.choice(routes)
    respuesta_aleatoria = routes[2]

    sendMessageToRoutesVotingQueue(respuesta_aleatoria)

    # Simular un error HTTP si la respuesta es un error
    if "error" in respuesta_aleatoria:
        return jsonify(respuesta_aleatoria), 503

    return jsonify({
        "message": "Retorno de ruta con éxito",
        "routes": respuesta_aleatoria
    })


def sendMessageToRoutesVotingQueue(vote):
    params = pika.URLParameters(url)

    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue='routes_voting', durable=True)

    channel.basic_publish(
        exchange='',
        routing_key='routes_voting',
        body=json.dumps(vote),
        properties=pika.BasicProperties(
            delivery_mode=2,
        )
    )

    print("✅ Mensaje enviado!")
    connection.close()


if __name__ == '__main__':
    app.run(port=5003, debug=True)