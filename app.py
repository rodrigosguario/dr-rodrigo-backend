import os
import psycopg2 # Para a ligação ao banco de dados
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Configuração de CORS para permitir a comunicação com o seu frontend no Netlify
CORS(app)

# --- FUNÇÕES DO BANCO DE DADOS ---
def get_db_connection():
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

def inicializar_db():
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id SERIAL PRIMARY KEY,
                    titulo VARCHAR(255) NOT NULL,
                    conteudo TEXT NOT NULL,
                    data_criacao TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
        conn.close()
        print("Banco de dados inicializado. Tabela 'posts' verificada/criada.")
    else:
        print("Falha na conexão com o DB. A inicialização foi ignorada.")


# --- ROTAS DA API ---

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

@app.route('/api/admin/check-auth', methods=['GET', 'OPTIONS'])
def check_auth():
    if request.method == 'OPTIONS':
        return '', 204
    return jsonify({
        "authenticated": True,
        "user": { "email": "admin@example.com", "name": "Dr. Rodrigo Sguario" }
    })

# --- ROTAS ADICIONADAS PARA EVITAR ERROS 404 ---
@app.route('/api/settings/<path:subpath>', methods=['GET', 'OPTIONS'])
def get_settings(subpath):
    if request.method == 'OPTIONS':
        return '', 204
    # Devolve uma resposta padrão para qualquer rota de 'settings'
    return jsonify([]), 200

# --- ROTA PARA SALVAR POSTS (CORRIGIDA) ---
# O caminho foi alterado de /api/posts para /api/blog/posts para corresponder ao frontend
@app.route('/api/blog/posts', methods=['POST', 'OPTIONS'])
def criar_post():
    if request.method == 'OPTIONS':
        return '', 204
        
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Nenhum dado enviado'}), 400

    titulo = data.get('titulo')
    conteudo = data.get('conteudo')

    if not titulo or not conteudo:
        return jsonify({'message': 'Título e conteúdo são obrigatórios'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Erro de conexão com o banco de dados'}), 500
    
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO posts (titulo, conteudo) VALUES (%s, %s)",
                (titulo, conteudo)
            )
            conn.commit()
        return jsonify({'message': 'Post salvo com sucesso!'}), 201
    except Exception as e:
        print(f"Erro ao inserir no banco de dados: {e}")
        conn.rollback()
        return jsonify({'message': 'Erro ao salvar o post'}), 500
    finally:
        if conn:
            conn.close()


# --- INICIALIZAÇÃO DO BANCO DE DADOS ---
with app.app_context():
    inicializar_db()

# Execução da aplicação
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)