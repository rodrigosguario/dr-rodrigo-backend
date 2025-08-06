#!/usr/bin/env python3
"""
Teste simples para verificar se o código está funcionando
"""
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['https://sitecardiologia.netlify.app'])

@app.route('/')
def home():
    return jsonify({"message": "Backend funcionando!"})

@app.route('/api/test')
def test():
    return jsonify({
        "status": "success",
        "message": "API funcionando",
        "cors": "Configurado"
    })

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
