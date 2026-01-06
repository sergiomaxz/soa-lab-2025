from flask import Flask, jsonify
from flask_cors import CORS
import socket

app = Flask(__name__)
CORS(app)

@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    return jsonify({"id": user_id, "name": "Ivan Cyclist", "valid": True, "served_by": socket.gethostname()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)