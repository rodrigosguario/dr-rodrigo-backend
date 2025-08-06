#!/usr/bin/env python3
"""
Script para testar a função Flask diretamente
"""

from app import app, get_db_connection
import json

def test_flask_function():
    with app.app_context():
        try:
            # Testar conexão
            conn = get_db_connection()
            if not conn:
                print("❌ Falha na conexão com o banco")
                return
            
            print("✅ Conectado ao banco")
            
            # Verificar se é SQLite
            is_sqlite = hasattr(conn, 'row_factory')
            print(f"🔧 Tipo de banco: {'SQLite' if is_sqlite else 'PostgreSQL'}")
            
            # Testar consulta
            if is_sqlite:
                cur = conn.cursor()
                cur.execute("""
                    SELECT section_id, section_name, content_data, updated_at 
                    FROM site_content 
                    ORDER BY section_id
                """)
                content = cur.fetchall()
            else:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT section_id, section_name, content_data, updated_at 
                        FROM site_content 
                        ORDER BY section_id
                    """)
                    content = cur.fetchall()
                
                print(f"📊 Registros encontrados: {len(content)}")
                
                content_list = []
                for item in content:
                    content_list.append({
                        'section_id': item[0],
                        'section_name': item[1],
                        'content_data': json.loads(item[2]) if is_sqlite else item[2],
                        'updated_at': item[3] if is_sqlite else (item[3].isoformat() if item[3] else None)
                    })
                
                print("✅ Dados processados com sucesso!")
                print(f"📝 Primeira seção: {content_list[0]['section_id']}")
                
            conn.close()
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_flask_function() 