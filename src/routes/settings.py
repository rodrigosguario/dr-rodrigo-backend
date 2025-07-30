from flask import Blueprint, request, jsonify, session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from ..models.settings import SiteSettings, WhatsAppConfig, PageContent, ColorTheme
import json

settings_bp = Blueprint('settings', __name__)

# Configuração do banco de dados
engine = create_engine('sqlite:///site_data.db')
Session = sessionmaker(bind=engine)

def require_auth():
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    return None

@settings_bp.route('/api/settings/whatsapp', methods=['GET'])
def get_whatsapp_config():
    db_session = Session()
    try:
        config = db_session.query(WhatsAppConfig).first()
        if not config:
            # Criar configuração padrão
            config = WhatsAppConfig()
            db_session.add(config)
            db_session.commit()
        
        return jsonify(config.to_dict())
    finally:
        db_session.close()

@settings_bp.route('/api/settings/whatsapp', methods=['POST'])
def update_whatsapp_config():
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    db_session = Session()
    try:
        data = request.get_json()
        config = db_session.query(WhatsAppConfig).first()
        
        if not config:
            config = WhatsAppConfig()
            db_session.add(config)
        
        # Atualizar campos
        if 'phone_number' in data:
            config.phone_number = data['phone_number']
        if 'welcome_message' in data:
            config.welcome_message = data['welcome_message']
        if 'transplant_message' in data:
            config.transplant_message = data['transplant_message']
        if 'heart_failure_message' in data:
            config.heart_failure_message = data['heart_failure_message']
        if 'preventive_message' in data:
            config.preventive_message = data['preventive_message']
        if 'echo_message' in data:
            config.echo_message = data['echo_message']
        if 'widget_enabled' in data:
            config.widget_enabled = data['widget_enabled']
        if 'widget_position' in data:
            config.widget_position = data['widget_position']
        if 'widget_color' in data:
            config.widget_color = data['widget_color']
        
        db_session.commit()
        return jsonify({'success': True, 'config': config.to_dict()})
    except Exception as e:
        db_session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db_session.close()

@settings_bp.route('/api/settings/page-content', methods=['GET'])
def get_page_content():
    db_session = Session()
    try:
        page = request.args.get('page', 'all')
        
        if page == 'all':
            contents = db_session.query(PageContent).all()
        else:
            contents = db_session.query(PageContent).filter_by(page_name=page).all()
        
        return jsonify([content.to_dict() for content in contents])
    finally:
        db_session.close()

@settings_bp.route('/api/settings/page-content', methods=['POST'])
def update_page_content():
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    db_session = Session()
    try:
        data = request.get_json()
        
        # Buscar conteúdo existente
        content = db_session.query(PageContent).filter_by(
            page_name=data['page_name'],
            section_name=data['section_name']
        ).first()
        
        if not content:
            content = PageContent(
                page_name=data['page_name'],
                section_name=data['section_name']
            )
            db_session.add(content)
        
        content.content = data['content']
        content.content_type = data.get('content_type', 'text')
        content.is_active = data.get('is_active', True)
        
        db_session.commit()
        return jsonify({'success': True, 'content': content.to_dict()})
    except Exception as e:
        db_session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db_session.close()

@settings_bp.route('/api/settings/colors', methods=['GET'])
def get_color_themes():
    db_session = Session()
    try:
        themes = db_session.query(ColorTheme).all()
        active_theme = db_session.query(ColorTheme).filter_by(is_active=True).first()
        
        return jsonify({
            'themes': [theme.to_dict() for theme in themes],
            'active_theme': active_theme.to_dict() if active_theme else None
        })
    finally:
        db_session.close()

@settings_bp.route('/api/settings/colors', methods=['POST'])
def create_color_theme():
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    db_session = Session()
    try:
        data = request.get_json()
        
        # Se for para ativar um tema existente
        if 'activate_theme_id' in data:
            # Desativar todos os temas
            db_session.query(ColorTheme).update({'is_active': False})
            
            # Ativar o tema selecionado
            theme = db_session.query(ColorTheme).get(data['activate_theme_id'])
            if theme:
                theme.is_active = True
                db_session.commit()
                return jsonify({'success': True, 'active_theme': theme.to_dict()})
            else:
                return jsonify({'error': 'Tema não encontrado'}), 404
        
        # Criar novo tema
        theme = ColorTheme(
            theme_name=data['theme_name'],
            primary_color=data['primary_color'],
            secondary_color=data['secondary_color'],
            accent_color=data['accent_color'],
            background_color=data['background_color'],
            text_color=data['text_color'],
            is_active=data.get('is_active', False)
        )
        
        # Se for para ativar este tema, desativar os outros
        if theme.is_active:
            db_session.query(ColorTheme).update({'is_active': False})
        
        db_session.add(theme)
        db_session.commit()
        
        return jsonify({'success': True, 'theme': theme.to_dict()})
    except Exception as e:
        db_session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db_session.close()

@settings_bp.route('/api/settings/general', methods=['GET'])
def get_general_settings():
    db_session = Session()
    try:
        settings = db_session.query(SiteSettings).all()
        settings_dict = {}
        
        for setting in settings:
            if setting.setting_type == 'json':
                try:
                    settings_dict[setting.setting_key] = json.loads(setting.setting_value)
                except:
                    settings_dict[setting.setting_key] = setting.setting_value
            elif setting.setting_type == 'boolean':
                settings_dict[setting.setting_key] = setting.setting_value.lower() == 'true'
            else:
                settings_dict[setting.setting_key] = setting.setting_value
        
        return jsonify(settings_dict)
    finally:
        db_session.close()

@settings_bp.route('/api/settings/general', methods=['POST'])
def update_general_settings():
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    db_session = Session()
    try:
        data = request.get_json()
        
        for key, value in data.items():
            setting = db_session.query(SiteSettings).filter_by(setting_key=key).first()
            
            if not setting:
                setting = SiteSettings(setting_key=key)
                db_session.add(setting)
            
            # Determinar tipo do valor
            if isinstance(value, bool):
                setting.setting_type = 'boolean'
                setting.setting_value = str(value).lower()
            elif isinstance(value, (dict, list)):
                setting.setting_type = 'json'
                setting.setting_value = json.dumps(value)
            else:
                setting.setting_type = 'text'
                setting.setting_value = str(value)
        
        db_session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db_session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db_session.close()

# Rota para gerar URL do WhatsApp
@settings_bp.route('/api/whatsapp-url', methods=['POST'])
def generate_whatsapp_url():
    db_session = Session()
    try:
        data = request.get_json()
        service_type = data.get('service_type', 'general')
        
        config = db_session.query(WhatsAppConfig).first()
        if not config:
            config = WhatsAppConfig()
        
        # Selecionar mensagem baseada no tipo de serviço
        message_map = {
            'transplant': config.transplant_message,
            'heart_failure': config.heart_failure_message,
            'preventive': config.preventive_message,
            'echo': config.echo_message,
            'general': config.welcome_message
        }
        
        message = message_map.get(service_type, config.welcome_message)
        
        # Gerar URL do WhatsApp
        whatsapp_url = f"https://wa.me/{config.phone_number}?text={message}"
        
        return jsonify({
            'url': whatsapp_url,
            'phone': config.phone_number,
            'message': message
        })
    finally:
        db_session.close()

