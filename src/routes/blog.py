from flask import Blueprint, request, jsonify, session
from src.models.blog import BlogPost, BlogCategory, db
from src.models.admin import Admin
from src.routes.admin import login_required
from datetime import datetime

blog_bp = Blueprint('blog', __name__)

# Rotas públicas (frontend)

@blog_bp.route('/posts', methods=['GET'])
def get_posts():
    """Retorna posts publicados para o frontend"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        category = request.args.get('category')
        search = request.args.get('search')
        
        query = BlogPost.query.filter_by(is_published=True)
        
        if category:
            query = query.filter_by(category=category)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(db.or_(
                BlogPost.title.like(search_term),
                BlogPost.content.like(search_term),
                BlogPost.excerpt.like(search_term)
            ))
        
        query = query.order_by(BlogPost.published_at.desc())
        
        # Paginação
        posts = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'posts': [post.to_dict() for post in posts.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': posts.total,
                'pages': posts.pages,
                'has_next': posts.has_next,
                'has_prev': posts.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@blog_bp.route('/posts/<slug>', methods=['GET'])
def get_post_by_slug(slug):
    """Retorna um post específico pelo slug"""
    try:
        post = BlogPost.query.filter_by(slug=slug, is_published=True).first()
        
        if not post:
            return jsonify({'error': 'Post não encontrado'}), 404
        
        # Incrementa visualizações
        post.increment_views()
        db.session.commit()
        
        return jsonify({'post': post.to_dict(include_content=True)}), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@blog_bp.route('/posts/featured', methods=['GET'])
def get_featured_posts():
    """Retorna posts em destaque"""
    try:
        limit = request.args.get('limit', 3, type=int)
        posts = BlogPost.get_featured_posts(limit=limit)
        
        return jsonify({
            'posts': [post.to_dict() for post in posts]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@blog_bp.route('/categories', methods=['GET'])
def get_categories():
    """Retorna todas as categorias"""
    try:
        categories = BlogCategory.query.all()
        
        return jsonify({
            'categories': [category.to_dict() for category in categories]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

# Rotas administrativas

@blog_bp.route('/admin/posts', methods=['GET'])
@login_required
def admin_get_posts():
    """Retorna todos os posts para administração"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')  # 'published', 'draft', 'all'
        
        query = BlogPost.query
        
        if status == 'published':
            query = query.filter_by(is_published=True)
        elif status == 'draft':
            query = query.filter_by(is_published=False)
        
        query = query.order_by(BlogPost.created_at.desc())
        
        posts = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'posts': [post.to_dict() for post in posts.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': posts.total,
                'pages': posts.pages,
                'has_next': posts.has_next,
                'has_prev': posts.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@blog_bp.route('/admin/posts', methods=['POST'])
@login_required
def admin_create_post():
    """Cria um novo post"""
    try:
        data = request.get_json()
        
        if not data or not data.get('title') or not data.get('content'):
            return jsonify({'error': 'Título e conteúdo são obrigatórios'}), 400
        
        post = BlogPost(
            title=data['title'],
            content=data['content'],
            category=data.get('category', 'Geral'),
            author_id=session['admin_id'],
            excerpt=data.get('excerpt'),
            tags=data.get('tags')
        )
        
        if data.get('featured_image'):
            post.featured_image = data['featured_image']
        
        if data.get('is_featured'):
            post.is_featured = data['is_featured']
        
        # Se for para publicar imediatamente
        if data.get('publish', False):
            post.publish()
        
        db.session.add(post)
        db.session.commit()
        
        return jsonify({
            'message': 'Post criado com sucesso',
            'post': post.to_dict(include_content=True)
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@blog_bp.route('/admin/posts/<int:post_id>', methods=['GET'])
@login_required
def admin_get_post(post_id):
    """Retorna um post específico para edição"""
    try:
        post = BlogPost.query.get(post_id)
        
        if not post:
            return jsonify({'error': 'Post não encontrado'}), 404
        
        return jsonify({'post': post.to_dict(include_content=True)}), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@blog_bp.route('/admin/posts/<int:post_id>', methods=['PUT'])
@login_required
def admin_update_post(post_id):
    """Atualiza um post existente"""
    try:
        post = BlogPost.query.get(post_id)
        
        if not post:
            return jsonify({'error': 'Post não encontrado'}), 404
        
        data = request.get_json()
        
        # Atualiza campos
        if 'title' in data:
            post.title = data['title']
            post.slug = post.generate_slug()  # Regenera slug se título mudou
        
        if 'content' in data:
            post.content = data['content']
            post.read_time = post.calculate_read_time()
        
        if 'excerpt' in data:
            post.excerpt = data['excerpt']
        
        if 'category' in data:
            post.category = data['category']
        
        if 'tags' in data:
            post.tags = data['tags']
        
        if 'featured_image' in data:
            post.featured_image = data['featured_image']
        
        if 'is_featured' in data:
            post.is_featured = data['is_featured']
        
        post.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Post atualizado com sucesso',
            'post': post.to_dict(include_content=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@blog_bp.route('/admin/posts/<int:post_id>/publish', methods=['POST'])
@login_required
def admin_publish_post(post_id):
    """Publica ou despublica um post"""
    try:
        post = BlogPost.query.get(post_id)
        
        if not post:
            return jsonify({'error': 'Post não encontrado'}), 404
        
        data = request.get_json()
        publish = data.get('publish', True)
        
        if publish:
            post.publish()
            message = 'Post publicado com sucesso'
        else:
            post.unpublish()
            message = 'Post despublicado com sucesso'
        
        db.session.commit()
        
        return jsonify({
            'message': message,
            'post': post.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@blog_bp.route('/admin/posts/<int:post_id>', methods=['DELETE'])
@login_required
def admin_delete_post(post_id):
    """Exclui um post"""
    try:
        post = BlogPost.query.get(post_id)
        
        if not post:
            return jsonify({'error': 'Post não encontrado'}), 404
        
        db.session.delete(post)
        db.session.commit()
        
        return jsonify({'message': 'Post excluído com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@blog_bp.route('/admin/categories', methods=['GET'])
@login_required
def admin_get_categories():
    """Retorna todas as categorias para administração"""
    try:
        categories = BlogCategory.query.all()
        
        return jsonify({
            'categories': [category.to_dict() for category in categories]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@blog_bp.route('/admin/categories', methods=['POST'])
@login_required
def admin_create_category():
    """Cria uma nova categoria"""
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'error': 'Nome da categoria é obrigatório'}), 400
        
        # Verifica se já existe
        existing = BlogCategory.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({'error': 'Categoria já existe'}), 400
        
        category = BlogCategory(
            name=data['name'],
            description=data.get('description'),
            color=data.get('color')
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'message': 'Categoria criada com sucesso',
            'category': category.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

