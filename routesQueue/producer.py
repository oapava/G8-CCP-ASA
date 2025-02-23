import pika
import json
import os
from config import RABBITMQ_HOST, RABBITMQ_QUEUE


url = os.environ.get('CLOUDAMQP_URL', RABBITMQ_HOST)

def publish_message(request):
    payload = request.get_json()
    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.basic_publish(
        exchange='routes_exchange',
        routing_key='',
        body=json.dumps(payload),
        properties=pika.BasicProperties(delivery_mode=2)
    )

    print(f"📦 Mensaje enviado : {payload}")

    connection.close()
    return {"status": "Message published"}
