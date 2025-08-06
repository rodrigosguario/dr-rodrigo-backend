#!/usr/bin/env python3
"""
Script para testar o banco de dados
"""

import sqlite3
import json

def test_database():
    try:
        # Conectar ao banco
        conn = sqlite3.connect('site_data.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        print("✅ Conectado ao banco SQLite")
        
        # Verificar tabelas
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cur.fetchall()
        print(f"📋 Tabelas encontradas: {[table[0] for table in tables]}")
        
        # Verificar conteúdo
        cur.execute("SELECT COUNT(*) FROM site_content")
        count = cur.fetchone()[0]
        print(f"📊 Registros em site_content: {count}")
        
        # Verificar dados
        cur.execute("SELECT section_id, section_name FROM site_content")
        sections = cur.fetchall()
        print("📝 Seções encontradas:")
        for section in sections:
            print(f"   - {section[0]}: {section[1]}")
        
        # Testar consulta específica
        cur.execute("SELECT content_data FROM site_content WHERE section_id = 'hero'")
        hero_data = cur.fetchone()
        if hero_data:
            print("✅ Dados do Hero encontrados")
            try:
                parsed_data = json.loads(hero_data[0])
                print(f"   Título: {parsed_data.get('title', 'N/A')}")
            except json.JSONDecodeError as e:
                print(f"❌ Erro ao decodificar JSON: {e}")
        else:
            print("❌ Dados do Hero não encontrados")
        
        conn.close()
        print("✅ Teste concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

if __name__ == "__main__":
    test_database() 