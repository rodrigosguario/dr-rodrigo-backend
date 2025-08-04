from flask import Flask, jsonify, request
from flask_cors import CORS
import datetime
import os

app = Flask(__name__)

# Aceita requisições de QUALQUER origem para teste
CORS(app, resources={ r"/api/*": { "origins": "*" } })

@app.route('/')
def home():
    return jsonify({"message": "API Backend funcionando!"})

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/admin/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 204
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        if email == 'admin@example.com' and password == 'admin123':
            return jsonify({"success": True, "token": "fake-jwt-token"})
        else:
            return jsonify({"success": False, "error": "Credenciais inválidas"}), 401
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)