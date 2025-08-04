from src.models.user import db
from datetime import datetime
import re

class BlogPost(db.Model):
    __tablename__ = 'blog_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(250), unique=True, nullable=False)
    excerpt = db.Column(db.Text)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    tags = db.Column(db.String(500))  # Tags separadas por vírgula
    featured_image = db.Column(db.String(500))
    is_published = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    read_time = db.Column(db.Integer, default=5)  # Tempo de leitura em minutos
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    
    # Relacionamento com admin (autor)
    author_id = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=False)
    
    def __init__(self, title, content, category, author_id, excerpt=None, tags=None):
        self.title = title
        self.content = content
        self.category = category
        self.author_id = author_id
        self.excerpt = excerpt or self.generate_excerpt()
        self.tags = tags
        self.slug = self.generate_slug()
        self.read_time = self.calculate_read_time()
    
    def generate_slug(self):
        """Gera um slug único baseado no título"""
        # Remove acentos e caracteres especiais
        slug = re.sub(r'[^\w\s-]', '', self.title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        
        # Verifica se já existe um slug igual
        existing = BlogPost.query.filter_by(slug=slug).first()
        if existing and existing.id != self.id:
            counter = 1
            while BlogPost.query.filter_by(slug=f"{slug}-{counter}").first():
                counter += 1
            slug = f"{slug}-{counter}"
        
        return slug
    
    def generate_excerpt(self):
        """Gera um resumo automático do conteúdo"""
        if not self.content:
            return ""
        
        # Remove tags HTML se houver
        clean_content = re.sub(r'<[^>]+>', '', self.content)
        
        # Pega os primeiros 200 caracteres
        if len(clean_content) <= 200:
            return clean_content
        
        # Corta no último espaço antes de 200 caracteres
        excerpt = clean_content[:200]
        last_space = excerpt.rfind(' ')
        if last_space > 0:
            excerpt = excerpt[:last_space]
        
        return excerpt + "..."
    
    def calculate_read_time(self):
        """Calcula o tempo de leitura baseado no conteúdo"""
        if not self.content:
            return 1
        
        # Remove tags HTML
        clean_content = re.sub(r'<[^>]+>', '', self.content)
        word_count = len(clean_content.split())
        
        # Assume 200 palavras por minuto
        read_time = max(1, round(word_count / 200))
        return read_time
    
    def publish(self):
        """Publica o post"""
        self.is_published = True
        self.published_at = datetime.utcnow()
    
    def unpublish(self):
        """Despublica o post"""
        self.is_published = False
        self.published_at = None
    
    def increment_views(self):
        """Incrementa o contador de visualizações"""
        self.views += 1
    
    def get_tags_list(self):
        """Retorna as tags como lista"""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def set_tags_from_list(self, tags_list):
        """Define as tags a partir de uma lista"""
        if tags_list:
            self.tags = ', '.join(tags_list)
        else:
            self.tags = None
    
    def to_dict(self, include_content=False):
        """Converte o objeto para dicionário"""
        data = {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'excerpt': self.excerpt,
            'category': self.category,
            'tags': self.get_tags_list(),
            'featured_image': self.featured_image,
            'is_published': self.is_published,
            'is_featured': self.is_featured,
            'read_time': self.read_time,
            'views': self.views,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'author_id': self.author_id
        }
        
        if include_content:
            data['content'] = self.content
        
        return data
    
    @staticmethod
    def get_published_posts(limit=None, category=None):
        """Retorna posts publicados"""
        query = BlogPost.query.filter_by(is_published=True).order_by(BlogPost.published_at.desc())
        
        if category:
            query = query.filter_by(category=category)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_featured_posts(limit=3):
        """Retorna posts em destaque"""
        return BlogPost.query.filter_by(is_published=True, is_featured=True)\
                           .order_by(BlogPost.published_at.desc())\
                           .limit(limit).all()
    
    @staticmethod
    def search_posts(query_text):
        """Busca posts por título ou conteúdo"""
        search_term = f"%{query_text}%"
        return BlogPost.query.filter_by(is_published=True)\
                           .filter(db.or_(
                               BlogPost.title.like(search_term),
                               BlogPost.content.like(search_term),
                               BlogPost.excerpt.like(search_term)
                           ))\
                           .order_by(BlogPost.published_at.desc()).all()
    
    def __repr__(self):
        return f'<BlogPost {self.title}>'


class BlogCategory(db.Model):
    __tablename__ = 'blog_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#3B82F6')  # Cor hex
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, name, description=None, color=None):
        self.name = name
        self.description = description
        if color:
            self.color = color
        self.slug = self.generate_slug()
    
    def generate_slug(self):
        """Gera um slug baseado no nome"""
        slug = re.sub(r'[^\w\s-]', '', self.name.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'color': self.color,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def create_default_categories():
        """Cria categorias padrão se não existirem"""
        default_categories = [
            {'name': 'Transplante Cardíaco', 'description': 'Artigos sobre transplante cardíaco', 'color': '#EF4444'},
            {'name': 'Insuficiência Cardíaca', 'description': 'Conteúdo sobre insuficiência cardíaca', 'color': '#3B82F6'},
            {'name': 'Prevenção', 'description': 'Dicas de prevenção cardiovascular', 'color': '#10B981'},
            {'name': 'Exames', 'description': 'Informações sobre exames cardiológicos', 'color': '#8B5CF6'},
            {'name': 'Tratamentos', 'description': 'Opções de tratamento', 'color': '#F59E0B'},
            {'name': 'Estilo de Vida', 'description': 'Dicas de vida saudável', 'color': '#06B6D4'}
        ]
        
        for cat_data in default_categories:
            existing = BlogCategory.query.filter_by(name=cat_data['name']).first()
            if not existing:
                category = BlogCategory(
                    name=cat_data['name'],
                    description=cat_data['description'],
                    color=cat_data['color']
                )
                db.session.add(category)
        
        db.session.commit()
    
    def __repr__(self):
        return f'<BlogCategory {self.name}>'

