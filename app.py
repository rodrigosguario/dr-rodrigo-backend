from flask import Flask, jsonify, request
from flask_cors import CORS
import datetime
import os

app = Flask(__name__)

# Configuração de CORS simplificada para garantir funcionamento
CORS(app)

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
        
        username = data.get('username')
        password = data.get('password')

        if username == 'admin@example.com' and password == 'admin123':
            return jsonify({
                "success": True, 
                "token": "fake-jwt-token-for-login",
                "user": { "email": "admin@example.com", "name": "Dr. Rodrigo Sguario" }
            })
        else:
            return jsonify({"success": False, "error": "Credenciais inválidas"}), 401
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# --- ROTA DE VERIFICAÇÃO DE AUTENTICAÇÃO (ADICIONADA DE VOLTA) ---
@app.route('/api/admin/check-auth', methods=['GET', 'OPTIONS'])
def check_auth():
    if request.method == 'OPTIONS':
        return '', 204
    
    # Para este teste, vamos assumir que qualquer pedido com um token é válido.
    # O seu frontend envia um cabeçalho 'Authorization'.
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith("Bearer "):
        return jsonify({
            "authenticated": True,
            "user": { "email": "admin@example.com", "name": "Dr. Rodrigo Sguario" }
        })
    else:
        # Se não houver token, não está autenticado
        return jsonify({"authenticated": False}), 401

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
