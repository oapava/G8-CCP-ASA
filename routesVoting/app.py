import pika
import os
import json

CLOUDAMQP_URL = os.environ.get(
    'CLOUDAMQP_URL', 'amqps://wvvfljaz:w9AfQi2yFo_obuplLkkV8HjKNrt7GA3M@moose.rmq.cloudamqp.com/wvvfljaz')

params = pika.URLParameters(CLOUDAMQP_URL)
connection = pika.BlockingConnection(params)
channel = connection.channel()
voting = []

channel.queue_declare(queue='routes_voting', durable=True)

def callback(ch, method, properties, body):
    resultado_final = json.loads(body.decode())
    voting.append(resultado_final)
    #print(f"✅ Resultado validado recibido: {resultado_final}")
    validate_vote()

def validate_vote():
    if len(voting) == 3:
        serializados = [json.dumps(voto, sort_keys=True) for voto in voting]

        valores_unicos = set(serializados)

        if len(valores_unicos) == 1:
            print(f"✅ Los 3 mensajes son IGUALES: {voting[0]}")
        else:
            print(f"❌ Hay diferencias. {len(valores_unicos)} valores únicos:")
            for i, voto in enumerate(voting):
                print(f"Voto {i+1}: {voto}")

        voting.clear()

channel.basic_consume(
    queue='routes_voting',
    on_message_callback=callback,
    auto_ack=True
)

print("🔄 Esperando mensajes validados...")
channel.start_consuming()
