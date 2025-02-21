from flask import Flask, jsonify
import requests
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

ROUTE_SERVICES = [
    'http://localhost:5001/route',
    'http://localhost:5002/route',
    'http://localhost:5003/route',
]

@app.route('/api/route')
def proxy_route():
    with ThreadPoolExecutor() as executor:
        resultados = list(executor.map(consultar_servicio, ROUTE_SERVICES))

    # Filtrar las respuestas válidas (status 200)
    exitosos = [res for res in resultados if res['status'] == 200]

    if not exitosos:
        return jsonify({"error": "Ningún servicio respondió correctamente"}), 503

    return jsonify({
        "message": "Respuestas de los microservicios",
        "results": exitosos
    })

def consultar_servicio(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {"status": 200, "data": data, "url": url}
        else:
            return {"status": response.status_code, "url": url}
    except requests.RequestException as e:
        return {"status": 500, "url": url, "error": str(e)}


if __name__ == '__main__':
    app.run(port=5000, debug=True)
