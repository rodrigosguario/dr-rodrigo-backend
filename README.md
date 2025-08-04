# Dr. Rodrigo Sguario - Backend API

Backend Flask para o site do Dr. Rodrigo Sguario, cardiologista especialista em transplante cardíaco.

## 🚀 Deploy no Render

Este projeto está configurado para deploy automático no Render.

### Configurações:
- **Runtime:** Python 3.11
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn --bind 0.0.0.0:$PORT src.main:app`

### Funcionalidades:
- ✅ Sistema de autenticação
- ✅ APIs do painel administrativo
- ✅ Sistema de blog
- ✅ Configurações dinâmicas
- ✅ CORS configurado para frontend

### Credenciais padrão:
- **Usuário:** admin
- **Senha:** admin123

### Endpoints principais:
- `/` - Status da API
- `/health` - Health check
- `/api/admin/*` - APIs administrativas
- `/api/blog/*` - APIs do blog
- `/api/settings/*` - APIs de configurações

## 🔧 Desenvolvimento local

```bash
pip install -r requirements.txt
python src/main.py
```

## 📱 Frontend

O frontend está hospedado no Netlify e se conecta com esta API.

