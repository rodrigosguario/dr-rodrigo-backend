# Configuração local para desenvolvimento
import os

# Configurações do Flask
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'

# Configurações de segurança
os.environ['SECRET_KEY'] = 'dev-secret-key-change-in-production'

print("Configuração local carregada!") 