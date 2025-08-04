from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class SiteSettings(Base):
    __tablename__ = 'site_settings'
    
    id = Column(Integer, primary_key=True)
    setting_key = Column(String(100), unique=True, nullable=False)
    setting_value = Column(Text, nullable=True)
    setting_type = Column(String(20), default='text')  # text, json, boolean, color
    description = Column(Text, nullable=True)
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self):
        return {
            'id': self.id,
            'setting_key': self.setting_key,
            'setting_value': self.setting_value,
            'setting_type': self.setting_type,
            'description': self.description,
            'updated_at': self.updated_at
        }

class WhatsAppConfig(Base):
    __tablename__ = 'whatsapp_config'
    
    id = Column(Integer, primary_key=True)
    phone_number = Column(String(20), nullable=False, default='5511933821515')
    welcome_message = Column(Text, default='Olá! Gostaria de agendar uma consulta com Dr. Rodrigo Sguario.')
    
    # Mensagens específicas por serviço
    transplant_message = Column(Text, default='Olá! Gostaria de agendar uma consulta sobre Transplante Cardíaco com Dr. Rodrigo Sguario.')
    heart_failure_message = Column(Text, default='Olá! Gostaria de agendar uma consulta sobre Insuficiência Cardíaca com Dr. Rodrigo Sguario.')
    preventive_message = Column(Text, default='Olá! Gostaria de agendar uma consulta de Cardiologia Preventiva com Dr. Rodrigo Sguario.')
    echo_message = Column(Text, default='Olá! Gostaria de agendar um Ecocardiograma com Dr. Rodrigo Sguario.')
    
    # Configurações do widget
    widget_enabled = Column(Boolean, default=True)
    widget_position = Column(String(20), default='bottom-right')  # bottom-right, bottom-left
    widget_color = Column(String(7), default='#25D366')
    
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self):
        return {
            'id': self.id,
            'phone_number': self.phone_number,
            'welcome_message': self.welcome_message,
            'transplant_message': self.transplant_message,
            'heart_failure_message': self.heart_failure_message,
            'preventive_message': self.preventive_message,
            'echo_message': self.echo_message,
            'widget_enabled': self.widget_enabled,
            'widget_position': self.widget_position,
            'widget_color': self.widget_color,
            'updated_at': self.updated_at
        }

class PageContent(Base):
    __tablename__ = 'page_content'
    
    id = Column(Integer, primary_key=True)
    page_name = Column(String(50), nullable=False)  # hero, about, services, etc
    section_name = Column(String(50), nullable=False)  # title, subtitle, description, etc
    content = Column(Text, nullable=False)
    content_type = Column(String(20), default='text')  # text, html, markdown
    is_active = Column(Boolean, default=True)
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self):
        return {
            'id': self.id,
            'page_name': self.page_name,
            'section_name': self.section_name,
            'content': self.content,
            'content_type': self.content_type,
            'is_active': self.is_active,
            'updated_at': self.updated_at
        }

class ColorTheme(Base):
    __tablename__ = 'color_themes'
    
    id = Column(Integer, primary_key=True)
    theme_name = Column(String(50), nullable=False)
    primary_color = Column(String(7), nullable=False)
    secondary_color = Column(String(7), nullable=False)
    accent_color = Column(String(7), nullable=False)
    background_color = Column(String(7), nullable=False)
    text_color = Column(String(7), nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self):
        return {
            'id': self.id,
            'theme_name': self.theme_name,
            'primary_color': self.primary_color,
            'secondary_color': self.secondary_color,
            'accent_color': self.accent_color,
            'background_color': self.background_color,
            'text_color': self.text_color,
            'is_active': self.is_active,
            'created_at': self.created_at
        }

