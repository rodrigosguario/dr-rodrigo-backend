from flask import Flask, jsonify, request
from flask_cors import CORS
import datetime
import os

# 1. INICIALIZAÇÃO DO FLASK
app = Flask(__name__)

# 2. CONFIGURAÇÃO DE CORS (ESSENCIAL PARA O SEU FRONTEND)
# Permite que seu site em 'netlify.app' se comunique com este backend.
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://sitecardiologia.netlify.app", "http://localhost:5173"], # Adicionado localhost para testes locais
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# 3. ROTA DE VERIFICAÇÃO DA API
# Ótima para um teste rápido e ver se o backend está no ar.
@app.route('/')
def home():
    return jsonify({
        "message": "API Backend Dr. Rodrigo Sguario funcionando!",
        "status": "OK",
        "timestamp": datetime.datetime.now().isoformat()
    })

# 4. ROTA DE HEALTH CHECK (IMPORTANTE PARA O RENDER)
# O Render usa esta rota para saber se sua aplicação está saudável.
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

# --- ROTAS DE AUTENTICAÇÃO ---

# 5. ROTA DE LOGIN (SIMPLIFICADA PARA DEBUG)
@app.route('/api/admin/login', methods=['POST', 'OPTIONS'])
def login():
    # O navegador envia uma requisição OPTIONS antes do POST para verificar o CORS.
    # Esta é a resposta para ela.
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.get_json()
        # ATENÇÃO: O frontend envia 'email', mas o código de exemplo usava 'username'.
        # Ajustado para 'email' para corresponder ao seu formulário.
        email = data.get('email')
        password = data.get('password')

        # Usando credenciais fixas para teste, eliminando a falha do banco de dados.
        # Futuramente, você pode substituir isso por uma conexão a um banco de dados em nuvem.
        if email == 'admin@example.com' and password == 'admin123':
            return jsonify({
                "success": True,
                "token": "fake-jwt-token-for-demo-purpose", # Token de exemplo
                "user": {
                    "email": "admin@example.com",
                    "name": "Dr. Rodrigo Sguario",
                    "role": "admin"
                }
            })
        else:
            # Retorna um erro claro se as credenciais estiverem erradas.
            return jsonify({"success": False, "error": "Credenciais inválidas"}), 401

    except Exception as e:
        # Captura outros erros, como JSON mal formatado.
        return jsonify({"success": False, "error": f"Erro no servidor: {str(e)}"}), 500

# 6. ROTA DE VERIFICAÇÃO DE AUTENTICAÇÃO
# O frontend pode usar esta rota para ver se o token do usuário ainda é válido.
@app.route('/api/admin/check-auth', methods=['GET', 'OPTIONS'])
def check_auth():
    if request.method == 'OPTIONS':
        return '', 204

    try:
        auth_header = request.headers.get('Authorization')
        
        # Simulação de verificação de token (aqui apenas checa se o header existe)
        if auth_header and auth_header.startswith("Bearer "):
            # Em um app real, você decodificaria e validaria o token JWT aqui.
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

# 7. EXECUÇÃO DA APLICAÇÃO (CONFIGURADO PARA O RENDER)
if __name__ == '__main__':
    # Pega a porta da variável de ambiente 'PORT', com 5000 como padrão para testes locais.
    port = int(os.environ.get('PORT', 5000))
    # Roda no host '0.0.0.0' para ser acessível externamente no Render.
    app.run(host='0.0.0.0', port=port)