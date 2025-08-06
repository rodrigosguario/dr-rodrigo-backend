import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# Configuração de CORS para permitir a comunicação com o seu frontend no Netlify
CORS(app)

# --- FUNÇÕES DO BANCO DE DADOS ---
def get_db_connection():
    try:
        # Verificar se a variável de ambiente existe
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("DATABASE_URL não configurada")
            return None
        
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

def inicializar_db():
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                # Tabela de posts (já existente)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS posts (
                        id SERIAL PRIMARY KEY,
                        titulo VARCHAR(255) NOT NULL,
                        conteudo TEXT NOT NULL,
                        data_criacao TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            
                # Tabela para conteúdo das seções do site
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS site_content (
                        id SERIAL PRIMARY KEY,
                        section_id VARCHAR(100) NOT NULL UNIQUE,
                        section_name VARCHAR(255) NOT NULL,
                        content_data JSONB NOT NULL,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Tabela para configurações do site
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS site_settings (
                        id SERIAL PRIMARY KEY,
                        setting_key VARCHAR(100) NOT NULL UNIQUE,
                        setting_value JSONB NOT NULL,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Tabela para avaliações importadas
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS reviews (
                        id SERIAL PRIMARY KEY,
                        source VARCHAR(50) NOT NULL,
                        external_id VARCHAR(255),
                        author_name VARCHAR(255) NOT NULL,
                        rating INTEGER NOT NULL,
                        comment TEXT,
                        date_created TIMESTAMP WITH TIME ZONE,
                        imported_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE
                    );
                """)
            
                # Inserir dados padrão COMPLETOS para todas as seções do site
                default_content = [
                ('hero', 'Seção Principal', {
                    "title": "Dr. Rodrigo Sguario",
                    "subtitle": "Cardiologista Especialista em Transplante Cardíaco",
                    "description": "Especialista em cardiologia com foco em transplante cardíaco e insuficiência cardíaca avançada.",
                    "cta_text": "Agendar Consulta",
                    "cta_link": "#contact",
                    "achievements": [
                        {"icon": "Heart", "title": "Referência em Transplante", "description": "Liderança e experiência em transplantes cardíacos"},
                        {"icon": "Award", "title": "Tecnologia Avançada", "description": "Equipamentos de última geração para diagnósticos precisos"},
                        {"icon": "Users", "title": "Atendimento Humanizado", "description": "Cuidado focado no paciente, com empatia e atenção"}
                    ],
                    "stats": [
                        {"number": "500+", "label": "Pacientes Atendidos"},
                        {"number": "15+", "label": "Anos de Experiência"},
                        {"number": "5.0", "label": "Avaliação Média", "icon": "Star"},
                        {"number": "24h", "label": "Suporte Emergencial"}
                    ]
                }),
                ('about', 'Sobre o Médico', {
                    "title": "Sobre o Dr. Rodrigo",
                    "description": "Médico cardiologista com ampla experiência em transplante cardíaco e cuidado humanizado.",
                    "education": [
                        {"institution": "Instituto do Coração (InCor) - USP-SP", "degree": "Especialização em Insuficiência Cardíaca e Transplante", "period": "2023-2024", "description": "Centro de referência em cardiologia da América Latina"},
                        {"institution": "UNICAMP", "degree": "Residência em Cardiologia", "period": "2021-2023", "description": "Formação especializada em cardiologia clínica e intervencionista"},
                        {"institution": "Universidade Federal de Pelotas (UFPel)", "degree": "Graduação em Medicina", "period": "2015-2020", "description": "Formação médica com foco humanizado"}
                    ],
                    "specialties": [
                        "Transplante Cardíaco",
                        "Insuficiência Cardíaca Avançada", 
                        "Cardiologia Preventiva",
                        "Ecocardiografia",
                        "Cateterismo Cardíaco",
                        "Reabilitação Cardíaca"
                    ],
                    "values": [
                        {"icon": "Heart", "title": "Formação de Excelência", "description": "InCor-USP, UNICAMP e UFPel. Formação acadêmica completa."},
                        {"icon": "Users", "title": "Foco no Paciente", "description": "Cuidado centrado nas necessidades individuais de cada paciente."},
                        {"icon": "BookOpen", "title": "Atualização Constante", "description": "Sempre em busca das mais recentes inovações em cardiologia."}
                    ]
                }),
                ('services', 'Serviços', {
                    "title": "Serviços Oferecidos",
                    "description": "Cuidado cardiológico completo e personalizado para cada paciente.",
                    "services": [
                        {"name": "Transplante Cardíaco", "description": "Avaliação, indicação e acompanhamento para transplante cardíaco", "icon": "Heart"},
                        {"name": "Insuficiência Cardíaca", "description": "Tratamento especializado para insuficiência cardíaca avançada", "icon": "Activity"},
                        {"name": "Cardiologia Preventiva", "description": "Prevenção e controle de fatores de risco cardiovascular", "icon": "Shield"},
                        {"name": "Ecocardiografia", "description": "Exames de imagem cardíaca com tecnologia avançada", "icon": "Monitor"},
                        {"name": "Cateterismo Cardíaco", "description": "Procedimentos diagnósticos e terapêuticos invasivos", "icon": "Zap"},
                        {"name": "Reabilitação Cardíaca", "description": "Programa de recuperação e prevenção secundária", "icon": "TrendingUp"}
                    ]
                }),
                ('contact', 'Contato', {
                    "title": "Entre em Contato",
                    "description": "Agende sua consulta ou entre em contato conosco",
                    "phone": "(11) 99999-9999",
                    "email": "contato@drrodrigosguario.com.br",
                    "address": "São Paulo, SP",
                    "hours": "Segunda a Sexta: 8h às 18h",
                    "emergency": "24h para casos de emergência"
                })
            ]
            
            # Inserir conteúdo padrão
            for section_id, section_name, content_data in default_content:
                cur.execute("""
                    INSERT INTO site_content (section_id, section_name, content_data) 
                    VALUES (%s, %s, %s)
                    ON CONFLICT (section_id) DO NOTHING;
                """, (section_id, section_name, json.dumps(content_data)))
            
                # Inserir configurações padrão
                default_settings = [
                ('doctor_info', {
                    "name": "Dr. Rodrigo Sguario",
                    "specialty": "Cardiologista",
                    "crm": "CRM/SP 123456",
                    "phone": "(11) 99999-9999",
                    "email": "contato@drrodrigosguario.com.br"
                }),
                ('clinic_info', {
                    "name": "Clínica Cardiológica",
                    "address": "São Paulo, SP",
                    "phone": "(11) 3333-4444",
                    "hours": "Segunda a Sexta: 8h às 18h"
                }),
                ('social_media', {
                    "instagram": "",
                    "facebook": "",
                    "linkedin": "",
                    "whatsapp": "(11) 99999-9999"
                }),
                ('site_config', {
                    "theme_color": "#1e293b",
                    "accent_color": "#d4af37",
                    "show_reviews": True,
                    "auto_import_reviews": False
                })
            ]
            
                for setting_key, setting_value in default_settings:
                    cur.execute("""
                        INSERT INTO site_settings (setting_key, setting_value) 
                        VALUES (%s, %s)
                        ON CONFLICT (setting_key) DO NOTHING;
                    """, (setting_key, json.dumps(setting_value)))
                
                conn.commit()
                conn.close()
                print("Banco de dados inicializado. Todas as tabelas do CMS verificadas/criadas.")
        except Exception as e:
            print(f"Erro ao inicializar banco de dados: {e}")
            if conn:
                conn.close()
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
def get_settings_fallback(subpath):
    if request.method == 'OPTIONS':
        return '', 204
    # Devolve uma resposta padrão para qualquer rota de 'settings'
    return jsonify([]), 200

# --- ROTAS CRUD COMPLETAS PARA POSTS ---

# CREATE - Criar novo post
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
                "INSERT INTO posts (titulo, conteudo) VALUES (%s, %s) RETURNING id",
                (titulo, conteudo)
            )
            post_id = cur.fetchone()[0]
            conn.commit()
        return jsonify({'message': 'Post salvo com sucesso!', 'id': post_id}), 201
    except Exception as e:
        print(f"Erro ao inserir no banco de dados: {e}")
        conn.rollback()
        return jsonify({'message': 'Erro ao salvar o post'}), 500
    finally:
        if conn:
            conn.close()

# READ - Listar todos os posts
@app.route('/api/blog/posts', methods=['GET', 'OPTIONS'])
def listar_posts():
    if request.method == 'OPTIONS':
        return '', 204
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Erro de conexão com o banco de dados'}), 500
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, titulo, conteudo, data_criacao 
                FROM posts 
                ORDER BY data_criacao DESC
            """)
            posts = cur.fetchall()
            
            posts_list = []
            for post in posts:
                posts_list.append({
                    'id': post[0],
                    'titulo': post[1],
                    'conteudo': post[2],
                    'data_criacao': post[3].isoformat() if post[3] else None
                })
            
        return jsonify(posts_list), 200
    except Exception as e:
        print(f"Erro ao buscar posts: {e}")
        return jsonify({'message': 'Erro ao carregar posts'}), 500
    finally:
        if conn:
            conn.close()

# READ - Buscar post específico por ID
@app.route('/api/blog/posts/<int:post_id>', methods=['GET', 'OPTIONS'])
def buscar_post(post_id):
    if request.method == 'OPTIONS':
        return '', 204
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Erro de conexão com o banco de dados'}), 500
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, titulo, conteudo, data_criacao 
                FROM posts 
                WHERE id = %s
            """, (post_id,))
            post = cur.fetchone()
            
            if not post:
                return jsonify({'message': 'Post não encontrado'}), 404
            
            post_data = {
                'id': post[0],
                'titulo': post[1],
                'conteudo': post[2],
                'data_criacao': post[3].isoformat() if post[3] else None
            }
            
        return jsonify(post_data), 200
    except Exception as e:
        print(f"Erro ao buscar post: {e}")
        return jsonify({'message': 'Erro ao carregar post'}), 500
    finally:
        if conn:
            conn.close()

# UPDATE - Atualizar post existente
@app.route('/api/blog/posts/<int:post_id>', methods=['PUT', 'OPTIONS'])
def atualizar_post(post_id):
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
            # Verificar se o post existe
            cur.execute("SELECT id FROM posts WHERE id = %s", (post_id,))
            if not cur.fetchone():
                return jsonify({'message': 'Post não encontrado'}), 404
            
            # Atualizar o post
            cur.execute("""
                UPDATE posts 
                SET titulo = %s, conteudo = %s 
                WHERE id = %s
            """, (titulo, conteudo, post_id))
            conn.commit()
            
        return jsonify({'message': 'Post atualizado com sucesso!'}), 200
    except Exception as e:
        print(f"Erro ao atualizar post: {e}")
        conn.rollback()
        return jsonify({'message': 'Erro ao atualizar post'}), 500
    finally:
        if conn:
            conn.close()

# DELETE - Deletar post
@app.route('/api/blog/posts/<int:post_id>', methods=['DELETE', 'OPTIONS'])
def deletar_post(post_id):
    if request.method == 'OPTIONS':
        return '', 204
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Erro de conexão com o banco de dados'}), 500
    
    try:
        with conn.cursor() as cur:
            # Verificar se o post existe
            cur.execute("SELECT id FROM posts WHERE id = %s", (post_id,))
            if not cur.fetchone():
                return jsonify({'message': 'Post não encontrado'}), 404
            
            # Deletar o post
            cur.execute("DELETE FROM posts WHERE id = %s", (post_id,))
            conn.commit()
            
        return jsonify({'message': 'Post deletado com sucesso!'}), 200
    except Exception as e:
        print(f"Erro ao deletar post: {e}")
        conn.rollback()
        return jsonify({'message': 'Erro ao deletar post'}), 500
    finally:
        if conn:
            conn.close()

# --- ROTAS DO SISTEMA CMS ---

# CONTENT MANAGEMENT - Gerenciamento de conteúdo das seções
@app.route('/api/content', methods=['GET', 'OPTIONS'])
def get_all_content():
    if request.method == 'OPTIONS':
        return '', 204
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Erro de conexão com o banco de dados'}), 500
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT section_id, section_name, content_data, updated_at 
                FROM site_content 
                ORDER BY section_id
            """)
            content = cur.fetchall()
            
            content_list = []
            for item in content:
                content_list.append({
                    'section_id': item[0],
                    'section_name': item[1],
                    'content_data': item[2],
                    'updated_at': item[3].isoformat() if item[3] else None
                })
            
        return jsonify(content_list), 200
    except Exception as e:
        print(f"Erro ao buscar conteúdo: {e}")
        return jsonify({'message': 'Erro ao carregar conteúdo'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/content/<section_id>', methods=['GET', 'PUT', 'OPTIONS'])
def manage_section_content(section_id):
    if request.method == 'OPTIONS':
        return '', 204
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Erro de conexão com o banco de dados'}), 500
    
    try:
        if request.method == 'GET':
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT section_id, section_name, content_data, updated_at 
                    FROM site_content 
                    WHERE section_id = %s
                """, (section_id,))
                content = cur.fetchone()
                
                if not content:
                    return jsonify({'message': 'Seção não encontrada'}), 404
                
                content_data = {
                    'section_id': content[0],
                    'section_name': content[1],
                    'content_data': content[2],
                    'updated_at': content[3].isoformat() if content[3] else None
                }
                
            return jsonify(content_data), 200
            
        elif request.method == 'PUT':
            data = request.get_json()
            if not data or 'content_data' not in data:
                return jsonify({'message': 'Dados de conteúdo são obrigatórios'}), 400
            
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE site_content 
                    SET content_data = %s, updated_at = CURRENT_TIMESTAMP 
                    WHERE section_id = %s
                """, (json.dumps(data['content_data']), section_id))
                
                if cur.rowcount == 0:
                    return jsonify({'message': 'Seção não encontrada'}), 404
                
                conn.commit()
                
            return jsonify({'message': 'Conteúdo atualizado com sucesso!'}), 200
            
    except Exception as e:
        print(f"Erro ao gerenciar conteúdo: {e}")
        conn.rollback()
        return jsonify({'message': 'Erro ao processar conteúdo'}), 500
    finally:
        if conn:
            conn.close()

# SETTINGS MANAGEMENT - Gerenciamento de configurações
@app.route('/api/settings', methods=['GET', 'OPTIONS'])
def get_all_settings():
    if request.method == 'OPTIONS':
        return '', 204
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Erro de conexão com o banco de dados'}), 500
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT setting_key, setting_value, updated_at 
                FROM site_settings 
                ORDER BY setting_key
            """)
            settings = cur.fetchall()
            
            settings_dict = {}
            for setting in settings:
                settings_dict[setting[0]] = {
                    'value': setting[1],
                    'updated_at': setting[2].isoformat() if setting[2] else None
                }
            
        return jsonify(settings_dict), 200
    except Exception as e:
        print(f"Erro ao buscar configurações: {e}")
        return jsonify({'message': 'Erro ao carregar configurações'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/settings/<setting_key>', methods=['GET', 'PUT', 'OPTIONS'])
def manage_setting(setting_key):
    if request.method == 'OPTIONS':
        return '', 204
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Erro de conexão com o banco de dados'}), 500
    
    try:
        if request.method == 'GET':
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT setting_value, updated_at 
                    FROM site_settings 
                    WHERE setting_key = %s
                """, (setting_key,))
                setting = cur.fetchone()
                
                if not setting:
                    return jsonify({'message': 'Configuração não encontrada'}), 404
                
                setting_data = {
                    'key': setting_key,
                    'value': setting[0],
                    'updated_at': setting[1].isoformat() if setting[1] else None
                }
                
            return jsonify(setting_data), 200
            
        elif request.method == 'PUT':
            data = request.get_json()
            if not data or 'value' not in data:
                return jsonify({'message': 'Valor da configuração é obrigatório'}), 400
            
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE site_settings 
                    SET setting_value = %s, updated_at = CURRENT_TIMESTAMP 
                    WHERE setting_key = %s
                """, (json.dumps(data['value']), setting_key))
                
                if cur.rowcount == 0:
                    return jsonify({'message': 'Configuração não encontrada'}), 404
                
                conn.commit()
                
            return jsonify({'message': 'Configuração atualizada com sucesso!'}), 200
            
    except Exception as e:
        print(f"Erro ao gerenciar configuração: {e}")
        conn.rollback()
        return jsonify({'message': 'Erro ao processar configuração'}), 500
    finally:
        if conn:
            conn.close()

# REVIEWS MANAGEMENT - Gerenciamento de avaliações
@app.route('/api/reviews', methods=['GET', 'POST', 'OPTIONS'])
def manage_reviews():
    if request.method == 'OPTIONS':
        return '', 204
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Erro de conexão com o banco de dados'}), 500
    
    try:
        if request.method == 'GET':
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, source, author_name, rating, comment, date_created, is_active 
                    FROM reviews 
                    WHERE is_active = TRUE 
                    ORDER BY date_created DESC
                """)
                reviews = cur.fetchall()
                
                reviews_list = []
                for review in reviews:
                    reviews_list.append({
                        'id': review[0],
                        'source': review[1],
                        'author_name': review[2],
                        'rating': review[3],
                        'comment': review[4],
                        'date_created': review[5].isoformat() if review[5] else None,
                        'is_active': review[6]
                    })
                
            return jsonify(reviews_list), 200
            
        elif request.method == 'POST':
            data = request.get_json()
            required_fields = ['source', 'author_name', 'rating']
            
            if not data or not all(field in data for field in required_fields):
                return jsonify({'message': 'Campos obrigatórios: source, author_name, rating'}), 400
            
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO reviews (source, external_id, author_name, rating, comment, date_created) 
                    VALUES (%s, %s, %s, %s, %s, %s) 
                    RETURNING id
                """, (
                    data['source'],
                    data.get('external_id'),
                    data['author_name'],
                    data['rating'],
                    data.get('comment'),
                    data.get('date_created')
                ))
                review_id = cur.fetchone()[0]
                conn.commit()
                
            return jsonify({'message': 'Avaliação adicionada com sucesso!', 'id': review_id}), 201
            
    except Exception as e:
        print(f"Erro ao gerenciar avaliações: {e}")
        conn.rollback()
        return jsonify({'message': 'Erro ao processar avaliações'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/reviews/import', methods=['POST', 'OPTIONS'])
def import_reviews():
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.get_json()
    source = data.get('source', 'all') if data else 'all'
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Erro de conexão com o banco de dados'}), 500
    
    try:
        # Criar algumas avaliações de exemplo para teste
        # Em produção, seria substituído pela importação real
        sample_reviews = [
            {
                "patient_name": "Maria Silva",
                "rating": 5,
                "comment": "Dr. Rodrigo é um excelente profissional! Muito atencioso e competente. Recomendo a todos que precisam de um cardiologista de confiança.",
                "date": "2025-01-15",
                "source": "doctoralia",
                "verified": True
            },
            {
                "patient_name": "João Santos",
                "rating": 5,
                "comment": "Cardiologista excepcional. Me ajudou muito no tratamento da minha condição cardíaca. Profissional muito dedicado.",
                "date": "2025-01-10",
                "source": "google",
                "verified": True
            },
            {
                "patient_name": "Ana Costa",
                "rating": 4,
                "comment": "Ótimo atendimento e explicações claras sobre o tratamento. Dr. Rodrigo sempre muito paciente com as dúvidas.",
                "date": "2025-01-08",
                "source": "doctoralia",
                "verified": True
            },
            {
                "patient_name": "Carlos Oliveira",
                "rating": 5,
                "comment": "Médico muito competente e humano. Salvou minha vida com o tratamento adequado. Gratidão eterna!",
                "date": "2025-01-05",
                "source": "google",
                "verified": True
            },
            {
                "patient_name": "Lucia Ferreira",
                "rating": 5,
                "comment": "Excelente cardiologista! Atendimento personalizado e tratamento eficaz. Super recomendo!",
                "date": "2025-01-03",
                "source": "doctoralia",
                "verified": True
            }
        ]
        
        # Filtrar por fonte se especificado
        if source == 'doctoralia':
            all_reviews = [r for r in sample_reviews if r['source'] == 'doctoralia']
        elif source == 'google':
            all_reviews = [r for r in sample_reviews if r['source'] == 'google']
        else:
            all_reviews = sample_reviews
        
        # Importar para o banco
        imported_count = 0
        
        with conn.cursor() as cur:
            for review in all_reviews:
                # Verificar se a avaliação já existe
                cur.execute("""
                    SELECT id FROM reviews 
                    WHERE author_name = %s AND comment = %s AND source = %s
                """, (review['patient_name'], review['comment'], review['source']))
                
                existing = cur.fetchone()
                
                if not existing:
                    # Inserir nova avaliação
                    cur.execute("""
                        INSERT INTO reviews (source, author_name, rating, comment, date_created, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        review['source'],
                        review['patient_name'],
                        review['rating'],
                        review['comment'],
                        review['date'],
                        True  # Ativa por padrão
                    ))
                    imported_count += 1
        
        conn.commit()
        
        return jsonify({
            "success": True,
            "imported": imported_count,
            "total_found": len(all_reviews),
            "message": f"{imported_count} novas avaliações importadas com sucesso!",
            "source": source
        }), 200
        
    except Exception as e:
        print(f"Erro ao importar avaliações: {e}")
        conn.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao importar avaliações: {str(e)}',
            'imported': 0
        }), 500
    finally:
        if conn:
            conn.close()

# --- ROTAS ADICIONAIS PARA WORDPRESS CMS ---

@app.route('/api/site/content', methods=['GET', 'POST', 'OPTIONS'])
def wordpress_site_content():
    if request.method == 'OPTIONS':
        return '', 204
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Erro de conexão com o banco de dados'}), 500
    
    try:
        if request.method == 'GET':
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT section_id, content_data 
                    FROM site_content 
                    ORDER BY section_id
                """)
                content = cur.fetchall()
                
                content_dict = {}
                for item in content:
                    content_dict[item[0]] = item[1]
                
            return jsonify(content_dict), 200
            
        elif request.method == 'POST':
            data = request.get_json()
            if not data:
                return jsonify({'message': 'Nenhum dado enviado'}), 400
            
            with conn.cursor() as cur:
                for section_id, content_data in data.items():
                    cur.execute("""
                        INSERT INTO site_content (section_id, section_name, content_data) 
                        VALUES (%s, %s, %s)
                        ON CONFLICT (section_id) 
                        DO UPDATE SET content_data = %s, updated_at = CURRENT_TIMESTAMP
                    """, (
                        section_id, 
                        section_id.replace('_', ' ').title(), 
                        json.dumps(content_data),
                        json.dumps(content_data)
                    ))
                
                conn.commit()
                
            return jsonify({'message': 'Conteúdo do site atualizado com sucesso!'}), 200
            
    except Exception as e:
        print(f"Erro ao gerenciar conteúdo do site: {e}")
        conn.rollback()
        return jsonify({'message': 'Erro ao processar conteúdo do site'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/site/content/<section_id>', methods=['PUT', 'OPTIONS'])
def wordpress_update_section(section_id):
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.get_json()
    if not data or 'content_data' not in data:
        return jsonify({'message': 'Dados de conteúdo são obrigatórios'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Erro de conexão com o banco de dados'}), 500
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO site_content (section_id, section_name, content_data) 
                VALUES (%s, %s, %s)
                ON CONFLICT (section_id) 
                DO UPDATE SET content_data = %s, updated_at = CURRENT_TIMESTAMP
            """, (
                section_id,
                section_id.replace('_', ' ').title(),
                json.dumps(data['content_data']),
                json.dumps(data['content_data'])
            ))
            
            conn.commit()
            
        return jsonify({'message': 'Seção atualizada com sucesso!'}), 200
        
    except Exception as e:
        print(f"Erro ao atualizar seção: {e}")
        conn.rollback()
        return jsonify({'message': 'Erro ao atualizar seção'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/site/backup', methods=['POST', 'OPTIONS'])
def wordpress_create_backup():
    if request.method == 'OPTIONS':
        return '', 204
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Erro de conexão com o banco de dados'}), 500
    
    try:
        with conn.cursor() as cur:
            # Backup do conteúdo
            cur.execute("SELECT section_id, content_data FROM site_content")
            content_backup = cur.fetchall()
            
            # Backup das configurações
            cur.execute("SELECT setting_key, setting_value FROM site_settings")
            settings_backup = cur.fetchall()
            
            # Backup dos posts
            cur.execute("SELECT id, titulo, conteudo, data_criacao FROM posts")
            posts_backup = cur.fetchall()
            
            backup_data = {
                'timestamp': datetime.now().isoformat(),
                'content': {item[0]: item[1] for item in content_backup},
                'settings': {item[0]: item[1] for item in settings_backup},
                'posts': [
                    {
                        'id': item[0],
                        'titulo': item[1],
                        'conteudo': item[2],
                        'data_criacao': item[3].isoformat() if item[3] else None
                    }
                    for item in posts_backup
                ]
            }
            
        return jsonify({
            'success': True,
            'message': 'Backup criado com sucesso!',
            'backup': backup_data
        }), 200
        
    except Exception as e:
        print(f"Erro ao criar backup: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro ao criar backup: {str(e)}'
        }), 500
    finally:
        if conn:
            conn.close()

# --- INICIALIZAÇÃO DO BANCO DE DADOS ---
with app.app_context():
    try:
        inicializar_db()
    except Exception as e:
        print(f"Erro na inicialização do banco: {e}")
        # Continua mesmo se falhar

# Execução da aplicação
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)