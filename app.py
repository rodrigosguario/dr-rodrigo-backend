from flask import Flask, jsonify
from flask_cors import CORS

# Cria um app Flask simples
app = Flask(__name__)

# Aplica a configuração de CORS diretamente neste app simples
CORS(app, 
     supports_credentials=True,
     origins=["https://sitecardiologia.netlify.app"])

# Cria uma rota de teste simples
@app.route("/api/test")
def test_route():
    return jsonify({"message": "CORS test successful!"})

# Rota de health check para a Render
@app.route("/health")
def health_check():
    return jsonify({"status": "healthy"})

# Não precisa do if __name__ == '__main__' para a Render com Gunicorn