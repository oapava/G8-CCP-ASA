import pika
import json
import os
from config import RABBITMQ_HOST, RABBITMQ_QUEUE

url = os.environ.get('CLOUDAMQP_URL', RABBITMQ_HOST)

def publish_message(payload):
    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

    message = json.dumps(payload)
    channel.basic_publish(
        exchange="",
        routing_key=RABBITMQ_QUEUE,
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  
        ),
    )

    print(f"📦 Mensaje enviado : {payload}")

    connection.close()
    return {"status": "Message published"}
