from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash
from src.models.admin import Admin, db
from src.models.blog import BlogPost, BlogCategory
from datetime import datetime
import functools

admin_bp = Blueprint('admin', __name__)

def login_required(f):
    """Decorator para verificar se o usuário está logado"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return jsonify({'error': 'Login necessário'}), 401
        
        admin = Admin.query.get(session['admin_id'])
        if not admin or not admin.is_active:
            session.clear()
            return jsonify({'error': 'Usuário inválido'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/login', methods=['POST'])
def login():
    """Endpoint de login do administrador"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username e senha são obrigatórios'}), 400
        
        username = data['username']
        password = data['password']
        
        # Busca o administrador
        admin = Admin.query.filter_by(username=username).first()
        
        if not admin or not admin.check_password(password):
            return jsonify({'error': 'Credenciais inválidas'}), 401
        
        if not admin.is_active:
            return jsonify({'error': 'Conta desativada'}), 401
        
        # Atualiza último login e gera token de sessão
        admin.update_last_login()
        session_token = admin.generate_session_token()
        
        # Salva na sessão
        session['admin_id'] = admin.id
        session['session_token'] = session_token
        
        db.session.commit()
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'admin': admin.to_dict(),
            'session_token': session_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@admin_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Endpoint de logout"""
    try:
        admin = Admin.query.get(session['admin_id'])
        if admin:
            admin.session_token = None
            db.session.commit()
        
        session.clear()
        
        return jsonify({'message': 'Logout realizado com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@admin_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """Retorna o perfil do administrador logado"""
    try:
        admin = Admin.query.get(session['admin_id'])
        return jsonify({'admin': admin.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@admin_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """Atualiza o perfil do administrador"""
    try:
        data = request.get_json()
        admin = Admin.query.get(session['admin_id'])
        
        # Campos que podem ser atualizados
        if 'full_name' in data:
            admin.full_name = data['full_name']
        
        if 'email' in data:
            # Verifica se o email já existe
            existing = Admin.query.filter_by(email=data['email']).first()
            if existing and existing.id != admin.id:
                return jsonify({'error': 'Email já está em uso'}), 400
            admin.email = data['email']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Perfil atualizado com sucesso',
            'admin': admin.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@admin_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Altera a senha do administrador"""
    try:
        data = request.get_json()
        
        if not data or not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Senha atual e nova senha são obrigatórias'}), 400
        
        admin = Admin.query.get(session['admin_id'])
        
        # Verifica a senha atual
        if not admin.check_password(data['current_password']):
            return jsonify({'error': 'Senha atual incorreta'}), 400
        
        # Valida a nova senha
        new_password = data['new_password']
        if len(new_password) < 6:
            return jsonify({'error': 'Nova senha deve ter pelo menos 6 caracteres'}), 400
        
        # Atualiza a senha
        admin.set_password(new_password)
        db.session.commit()
        
        return jsonify({'message': 'Senha alterada com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@admin_bp.route('/dashboard/stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    """Retorna estatísticas para o dashboard"""
    try:
        # Estatísticas do blog
        total_posts = BlogPost.query.count()
        published_posts = BlogPost.query.filter_by(is_published=True).count()
        draft_posts = total_posts - published_posts
        
        # Posts mais visualizados
        popular_posts = BlogPost.query.filter_by(is_published=True)\
                                      .order_by(BlogPost.views.desc())\
                                      .limit(5).all()
        
        # Posts recentes
        recent_posts = BlogPost.query.order_by(BlogPost.created_at.desc())\
                                     .limit(5).all()
        
        # Total de visualizações
        total_views = db.session.query(db.func.sum(BlogPost.views)).scalar() or 0
        
        stats = {
            'blog': {
                'total_posts': total_posts,
                'published_posts': published_posts,
                'draft_posts': draft_posts,
                'total_views': total_views
            },
            'popular_posts': [post.to_dict() for post in popular_posts],
            'recent_posts': [post.to_dict() for post in recent_posts]
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500