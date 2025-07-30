from src.models.user import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets

class Admin(db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    session_token = db.Column(db.String(255))
    
    def __init__(self, username, email, password, full_name):
        self.username = username
        self.email = email
        self.full_name = full_name
        self.set_password(password)
    
    def set_password(self, password):
        """Define a senha do administrador com hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.password_hash, password)
    
    def generate_session_token(self):
        """Gera um token de sessão único"""
        self.session_token = secrets.token_urlsafe(32)
        return self.session_token
    
    def update_last_login(self):
        """Atualiza o timestamp do último login"""
        self.last_login = datetime.utcnow()
    
    def to_dict(self):
        """Converte o objeto para dicionário (sem dados sensíveis)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    @staticmethod
    def create_default_admin():
        """Cria um administrador padrão se não existir"""
        existing_admin = Admin.query.first()
        if not existing_admin:
            admin = Admin(
                username='admin',
                email='rodrigomrsguario.cardiologia@gmail.com',
                password='admin123',  # Senha temporária - deve ser alterada
                full_name='Dr. Rodrigo Sguario'
            )
            db.session.add(admin)
            db.session.commit()
            return admin
        return existing_admin
    
    def __repr__(self):
        return f'<Admin {self.username}>'

