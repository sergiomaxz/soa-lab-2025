from flask import Flask, request, jsonify
from flask_cors import CORS
import pika
import json
import requests
from auth_middleware import require_auth

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}) # CORS на рівні Flask

@app.route('/finish_ride', methods=['POST'])
@require_auth(scope="ride:write")  # <--- ЗАХИЩЕНИЙ ЕНДПОІНТ
def finish_ride():
    data = request.json
    # Логіка відправки в RabbitMQ...
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='ride_finished_queue')
    channel.basic_publish(exchange='', routing_key='ride_finished_queue', body=json.dumps(data))
    connection.close()
    return jsonify({"status": "Accepted", "saga": "Pending"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)