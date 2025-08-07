from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "Backend funcionando!"})

@app.route('/api/test')
def test():
    return jsonify({
        "status": "success", 
        "message": "API funcionando corretamente"
    })

@app.route('/api/site/content', methods=['GET'])
def get_content():
    return jsonify({
        "success": True,
        "data": {
            "hero": {
                "title": "Dr. Rodrigo Sguario",
                "subtitle": "Cardiologista Especialista"
            }
        }
    })

@app.route('/api/site/content', methods=['PUT'])
def save_content():
    return jsonify({
        "success": True,
        "message": "Conteúdo salvo com sucesso!"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
