#!/usr/bin/env python3
"""
Script para inicializar o banco de dados local
Dr. Rodrigo Sguario - Site de Cardiologia
"""

import sqlite3
import json
from datetime import datetime

def create_tables():
    """Cria as tabelas necessárias no banco SQLite"""
    conn = sqlite3.connect('site_data.db')
    cursor = conn.cursor()
    
    # Tabela de posts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            conteudo TEXT NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela para conteúdo das seções do site
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS site_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section_id TEXT NOT NULL UNIQUE,
            section_name TEXT NOT NULL,
            content_data TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela para configurações do site
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS site_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_key TEXT NOT NULL UNIQUE,
            setting_value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela para avaliações
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            external_id TEXT,
            author_name TEXT NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT,
            date_created TIMESTAMP,
            imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    conn.commit()
    print("✅ Tabelas criadas com sucesso!")
    return conn

def insert_default_data(conn):
    """Insere dados padrão nas tabelas"""
    cursor = conn.cursor()
    
    # Dados padrão para seções do site
    default_content = [
        ('hero', 'Seção Principal', json.dumps({
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
        })),
        ('about', 'Sobre o Médico', json.dumps({
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
        })),
        ('services', 'Serviços', json.dumps({
            "title": "Serviços Oferecidos",
            "description": "Cuidado cardiológico completo e personalizado para cada paciente.",
            "services": [
                {
                    "id": "transplant",
                    "title": "Transplante Cardíaco",
                    "description": "Avaliação completa para transplante cardíaco, acompanhamento pré e pós-operatório.",
                    "duration": "60-90 min",
                    "features": ["Avaliação pré-transplante", "Acompanhamento pós-transplante", "Manejo de rejeição", "Cuidados a longo prazo"]
                },
                {
                    "id": "heart_failure",
                    "title": "Insuficiência Cardíaca Avançada",
                    "description": "Tratamento especializado para insuficiência cardíaca em estágios avançados.",
                    "duration": "45-60 min",
                    "features": ["Otimização medicamentosa", "Terapia de ressincronização", "Dispositivos de assistência", "Monitoramento remoto"]
                },
                {
                    "id": "preventive",
                    "title": "Cardiologia Preventiva",
                    "description": "Prevenção e diagnóstico precoce de doenças cardiovasculares.",
                    "duration": "30-45 min",
                    "features": ["Avaliação de risco cardiovascular", "Check-up cardiológico", "Orientação nutricional", "Programa de exercícios"]
                },
                {
                    "id": "echo",
                    "title": "Ecocardiografia",
                    "description": "Exame de imagem não invasivo para avaliação detalhada da estrutura e função cardíaca.",
                    "duration": "30-45 min",
                    "features": ["Ecocardiografia transtorácica", "Ecocardiografia transesofágica", "Ecocardiografia de estresse", "Avaliação de função ventricular"]
                }
            ]
        })),
        ('contact', 'Contato', json.dumps({
            "title": "Entre em Contato",
            "subtitle": "Agende sua consulta ou tire suas dúvidas. Estamos aqui para cuidar da sua saúde cardíaca",
            "phone": "(11) 3382-1515",
            "whatsapp": "(11) 99999-9999",
            "email": "rodrigomrsguario.cardiologia@gmail.com",
            "address": {
                "street": "Av. Paulista, 1048, 18º andar",
                "district": "Bela Vista, São Paulo - SP",
                "cep": "CEP: 01310-100"
            },
            "hours": {
                "weekdays": "Segunda a Sexta: 8h às 18h",
                "saturday": "Sábado: 8h às 12h",
                "emergency": "Emergências: 24h"
            }
        }))
    ]
    
    # Inserir dados padrão
    for section_id, section_name, content_data in default_content:
        cursor.execute('''
            INSERT OR REPLACE INTO site_content (section_id, section_name, content_data)
            VALUES (?, ?, ?)
        ''', (section_id, section_name, content_data))
    
    # Configurações padrão
    default_settings = [
        ('social_media', json.dumps({
            "whatsapp": {
                "phone": "5511933821515",
                "messages": {
                    "transplant": "Olá! Gostaria de agendar uma consulta sobre Transplante Cardíaco com Dr. Rodrigo Sguario.",
                    "heart_failure": "Olá! Gostaria de agendar uma consulta sobre Insuficiência Cardíaca com Dr. Rodrigo Sguario.",
                    "preventive": "Olá! Gostaria de agendar uma consulta de Cardiologia Preventiva com Dr. Rodrigo Sguario.",
                    "echo": "Olá! Gostaria de agendar um Ecocardiograma com Dr. Rodrigo Sguario."
                }
            }
        })),
        ('site_info', json.dumps({
            "title": "Dr. Rodrigo Sguario - Cardiologista",
            "description": "Especialista em cardiologia com foco em transplante cardíaco e insuficiência cardíaca avançada.",
            "keywords": "cardiologista, transplante cardíaco, insuficiência cardíaca, São Paulo"
        }))
    ]
    
    for setting_key, setting_value in default_settings:
        cursor.execute('''
            INSERT OR REPLACE INTO site_settings (setting_key, setting_value)
            VALUES (?, ?)
        ''', (setting_key, setting_value))
    
    # Avaliações de exemplo
    sample_reviews = [
        ('doctoralia', 'ext_1', 'Maria Silva', 5, 'Excelente profissional! Dr. Rodrigo é muito atencioso e competente.', '2024-01-15'),
        ('google', 'ext_2', 'João Santos', 5, 'Recomendo muito! Tratamento excepcional e resultados excelentes.', '2024-01-10'),
        ('manual', None, 'Ana Costa', 4, 'Muito bom atendimento, recomendo!', '2024-01-05')
    ]
    
    for source, external_id, author_name, rating, comment, date_created in sample_reviews:
        cursor.execute('''
            INSERT OR REPLACE INTO reviews (source, external_id, author_name, rating, comment, date_created)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (source, external_id, author_name, rating, comment, date_created))
    
    conn.commit()
    print("✅ Dados padrão inseridos com sucesso!")

def main():
    """Função principal"""
    print("🚀 Inicializando banco de dados local...")
    
    try:
        # Criar tabelas
        conn = create_tables()
        
        # Inserir dados padrão
        insert_default_data(conn)
        
        # Fechar conexão
        conn.close()
        
        print("🎉 Banco de dados inicializado com sucesso!")
        print("📁 Arquivo: site_data.db")
        print("🔧 Próximo passo: Execute 'python app.py' para iniciar o servidor")
        
    except Exception as e:
        print(f"❌ Erro ao inicializar banco de dados: {e}")

if __name__ == "__main__":
    main() 