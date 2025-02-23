import functions_framework
import requests
import time
from datetime import datetime
import json
import random

@functions_framework.http
def main(request):
    path = request.path
    bucle()
    return jsonify({"Succes": "Monitoreando componente customer"}), 200

# URL del servicio
SERVICE_URL = "https://routes-queue-1075292097466.us-central1.run.app/customers"
INTERVAL_SECONDS = 10  

# Datos del cliente
DATA_CUSTOMER = [
    {
        "name": "Client E",
        "registry": "099298463484",
        "zone": "Norte",
        "country": "CO",
        "cluster": "MED"
    },{
        "registry": "099298463484",
        "zone": "Norte",
        "country": "CO",
        "cluster": "MED"
    }
] 

def check_service():
    try:
        start_time = time.time()
        
        response = requests.post(
            SERVICE_URL,
            json= random.choice(DATA_CUSTOMER) , 
            headers={
                "Content-Type": "application/json" 
            },
            timeout=5
        )
        end_time = time.time()

        response_time = round((end_time - start_time) * 1000, 2)
        status_code = response.status_code

        if status_code == 200 or status_code == 201:
            print(f"[{datetime.now()}] ✅ Servicio Activo | Tiempo de respuesta: {response_time} ms")
        else:
            print(f"[{datetime.now()}] ⚠️ Servicio responde con código {status_code} | Respuesta: {response.text}")

    except requests.ConnectionError:
        print(f"[{datetime.now()}] ❌ ERROR: No se pudo conectar al servicio")
    except requests.Timeout:
        print(f"[{datetime.now()}] ⏳ ERROR: El servicio tardó demasiado en responder")
    except Exception as e:
        print(f"[{datetime.now()}] ❗ ERROR Desconocido: {str(e)}")

def bucle():
    # Bucle de monitoreo
    print(f"🔍 Iniciando monitor para {SERVICE_URL} cada {INTERVAL_SECONDS} segundos...\n")
    while True:
        check_service()
        time.sleep(INTERVAL_SECONDS)