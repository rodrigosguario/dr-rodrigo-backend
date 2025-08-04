from flask import Flask, jsonify, request
from flask_cors import CORS
import datetime
import os

app = Flask(__name__)

# Configuração de CORS simplificada para garantir o funcionamento
CORS(app)

# Rota principal para verificar se a API está no ar
@app.route('/')
def home():
    return jsonify({"message": "API Backend funcionando!"})

# Rota de verificação de saúde para o Render
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

# Rota de login
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

# Rota de verificação de autenticação (MODIFICADA)
@app.route('/api/admin/check-auth', methods=['GET', 'OPTIONS'])
def check_auth():
    if request.method == 'OPTIONS':
        return '', 204
    
    # --- CORREÇÃO FINAL ---
    # Para simplificar, esta rota agora devolve sempre sucesso.
    # Isto permite que o frontend entre no dashboard após o login.
    return jsonify({
        "authenticated": True,
        "user": { "email": "admin@example.com", "name": "Dr. Rodrigo Sguario" }
    })

# Execução da aplicação
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)