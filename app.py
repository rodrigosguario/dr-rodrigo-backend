from flask import Flask, jsonify, request
from flask_cors import CORS
import datetime
import os

# 1. INICIALIZAÇÃO DO FLASK
app = Flask(__name__)

# 2. CONFIGURAÇÃO DE CORS (MODIFICADA PARA TESTE)
# A linha "origins" foi alterada para "*" (asterisco), que significa "aceitar requisições de QUALQUER origem".
# Isto é apenas para depuração. Não é seguro para um ambiente de produção final.
CORS(app, resources={
    r"/api/*": {
        "origins": "*", # MUDANÇA CRÍTICA PARA O TESTE
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# 3. ROTA DE VERIFICAÇÃO DA API
@app.route('/')
def home():
    return jsonify({
        "message": "API Backend Dr. Rodrigo Sguario funcionando!",
        "status": "OK",
        "timestamp": datetime.datetime.now().isoformat()
    })

# 4. ROTA DE HEALTH CHECK
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

# --- ROTAS DE AUTENTICAÇÃO (SEM ALTERAÇÕES) ---

# 5. ROTA DE LOGIN
@app.route('/api/admin/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if email == 'admin@example.com' and password == 'admin123':
            return jsonify({
                "success": True,
                "token": "fake-jwt-token-for-demo-purpose",
                "user": {
                    "email": "admin@example.com",
                    "name": "Dr. Rodrigo Sguario",
                    "role": "admin"
                }
            })
        else:
            return jsonify({"success": False, "error": "Credenciais inválidas"}), 401

    except Exception as e:
        return jsonify({"success": False, "error": f"Erro no servidor: {str(e)}"}), 500

# 6. ROTA DE VERIFICAÇÃO DE AUTENTICAÇÃO
@app.route('/api/admin/check-auth', methods=['GET', 'OPTIONS'])
def check_auth():
    if request.method == 'OPTIONS':
        return '', 204

    try:
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith("Bearer "):
            return jsonify({
                "authenticated": True,
                "user": {
                    "email": "admin@example.com",
                    "name": "Dr. Rodrigo Sguario"
                }
            })
        else:
            return jsonify({"authenticated": False}), 401
            
    except Exception as e:
        return jsonify({"authenticated": False, "error": str(e)}), 500

# 7. EXECUÇÃO DA APLICAÇÃO
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
<<<<<<< HEAD
    app.run(host='0.0.0.0', port=port)
=======
    # Roda no host '0.0.0.0' para ser acessível externamente no Render.
    app.run(host='0.0.0.0', port=port)
>>>>>>> cec630c47f6447a3975d9732f99bdf6cbcaa615e
