# Quick Start Guide

Guía rápida para levantar OpenTender Radar en 5 minutos.

## Opción rápida: Docker Compose

```bash
# 1. Clonar o descargar el proyecto
cd OpenTender

# 2. Levantar servicios
docker-compose up --build

# 3. En otra terminal, poblar datos
docker-compose exec backend python seed.py

# 4. Abrir navegador
# Frontend: http://localhost:5173
# API Docs: http://localhost:8000/docs
```

## Opción desarrollo local

### Backend

```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed.py
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Verificar instalación

1. Backend responde: `curl http://localhost:8000/health`
2. Frontend carga: `http://localhost:5173`
3. API docs: `http://localhost:8000/docs`

## Problemas comunes

**Error: puerto en uso**
- Backend: cambiar puerto en `uvicorn main:app --port 8001`
- Frontend: cambiar en `vite.config.js`

**Error: base de datos no encontrada**
- Ejecutar `python backend/seed.py` primero

**Error: CORS en frontend**
- Verificar que `VITE_API_URL` apunte a `http://localhost:8000`
