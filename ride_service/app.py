from flask import Flask, request, jsonify
from flask_cors import CORS
import pika
import json
import requests
from auth_middleware import require_auth

USER_SERVICE_URL = "http://user_service:5001/users/"

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}) # CORS на рівні Flask

def get_rabbit_connection():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    return connection

@app.route('/finish_ride', methods=['POST'])
@require_auth(scope="ride:write")  # <--- ЗАХИЩЕНИЙ ЕНДПОІНТ
def finish_ride():
    data = request.json

    user_id = data.get('user_id', -1)
    try:
        user_resp = requests.get(USER_SERVICE_URL + str(user_id))
        if user_resp.status_code != 200:
            return jsonify({"error": "User not found"}), 404
        user_info = user_resp.json()
    except Exception as e:
         return jsonify({"error": "User Service unavailable"}), 503
    
    # Логіка відправки в RabbitMQ...
    try:
        connection = get_rabbit_connection()
        channel = connection.channel()
        channel.queue_declare(queue='ride_finished_queue')
        
        message = {
            "ride_id": data.get("ride_id"),
            "user_id": user_id,
            "distance_km": data.get("distance_km"),
            "raw_points": data.get("points_count")
        }
        
        channel.basic_publish(exchange='', routing_key='ride_finished_queue', body=json.dumps(message))
        connection.close()
    except Exception as e:
        print(f"RabbitMQ Error: {e}")

    return jsonify({
        "status": "Accepted",
        "saga": "Pending",
        "user_verified_by": user_info['served_by']  # Покаже, який інстанс user_service відповів
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)