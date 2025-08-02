import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify
from flask_cors import CORS # Importamos o CORS aqui
from src.models.user import db
from src.models.admin import Admin
from src.models.blog import BlogPost, BlogCategory
from src.routes.user import user_bp
from src.routes.admin import admin_bp
from src.routes.blog import blog_bp
from src.routes.settings import settings_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dr-rodrigo-secret-key-2025')

# Configuração de CORS centralizada e comprovadamente funcional
CORS(app, 
     supports_credentials=True,
     origins=["https://sitecardiologia.netlify.app"])

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(blog_bp, url_prefix='/api/blog')
app.register_blueprint(settings_bp, url_prefix='/api')

# Configuração do banco de dados
database_path = os.path.join(os.path.dirname(__file__), 'database', 'app.db')
os.makedirs(os.path.dirname(database_path), exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{database_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Inicializar banco de dados
with app.app_context():
    db.create_all()
    
    # Criar administrador padrão
    Admin.create_default_admin()
    
    # Criar categorias padrão
    BlogCategory.create_default_categories()
    
    print("✅ API Backend inicializada com sucesso!")
    print("📧 Admin padrão: admin / admin123")
    print("🔄 Lembre-se de alterar a senha padrão!")

# Rota de status da API
@app.route('/')
def api_status():
    return jsonify({
        "status": "online",
        "message": "Dr. Rodrigo Sguario - API Backend",
        "version": "1.0.0"
    })

# Rota de health check para a Render
@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "version": "final-solution" # Versão final para confirmar o deploy
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)