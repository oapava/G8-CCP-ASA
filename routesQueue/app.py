from flask import Flask, request, jsonify
from producer import publish_message

app = Flask(__name__)

@app.route("/send", methods=["POST"])
def send_message():
    data = request.json
    print(f"📦 Recibiendo mensaje: {data}")
    result = publish_message(data)
    return jsonify(result), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
