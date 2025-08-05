import os
import psycopg2 # A nova biblioteca que instalámos
from flask import Flask, request, jsonify
from flask_cors import CORS # Importar o CORS

app = Flask(__name__)

# Configurar o CORS para permitir pedidos do seu frontend
# Substitua 'https://seu-site-frontend.onrender.com' pela URL real do seu site
CORS(app, resources={r"/api/*": {"origins": "*"}}) # Para já, vamos permitir todas as origens para facilitar os testes

# Função para obter a conexão com o banco de dados
def get_db_connection():
    try:
        # A variável DATABASE_URL foi configurada no ambiente do Render
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Função para criar a tabela se ela não existir
def inicializar_db():
    conn = get_db_connection()
    if conn:
        # 'with' garante que a conexão e o cursor são fechados no final
        with conn.cursor() as cur:
            # Vamos criar uma tabela simples para guardar posts de um blog
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

# Rota de login (a que você já tem)
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Nenhum dado enviado'}), 400

    email = data.get('email')
    password = data.get('password')

    # Lembre-se: esta é uma verificação insegura, apenas para demonstração
    if email == 'admin@example.com' and password == 'admin123':
        return jsonify({'message': 'Login bem-sucedido'}), 200
    else:
        return jsonify({'message': 'Credenciais inválidas'}), 401

# ---- NOVA ROTA PARA SALVAR DADOS ----
@app.route('/api/posts', methods=['POST'])
def criar_post():
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
        conn.rollback() # Desfaz a transação em caso de erro
        return jsonify({'message': 'Erro ao salvar o post'}), 500
    finally:
        if conn:
            conn.close()

# Executa a inicialização do DB uma vez quando a aplicação arranca
# Usamos um contexto de aplicação para garantir que tudo está pronto
with app.app_context():
    inicializar_db()

# Esta parte não é necessária no Render, mas é boa para testes locais
if __name__ == '__main__':
    # Usar a porta fornecida pelo Render ou 5000 para testes locais
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)