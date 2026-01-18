# Backend - OpenTender Radar

API FastAPI para gestionar y consultar licitaciones públicas.

## Estructura

- `main.py`: Endpoints de la API
- `models.py`: Modelos de datos (Pydantic + SQLAlchemy)
- `database.py`: Configuración de base de datos
- `scoring.py`: Motor de scoring
- `seed.py`: Script para poblar datos mock

## Desarrollo

```bash
# Instalar dependencias
pip install -r requirements.txt

# Poblar base de datos
python seed.py

# Iniciar servidor
uvicorn main:app --reload
```

## Endpoints principales

- `GET /tenders`: Lista paginada de licitaciones con filtros
- `GET /tenders/{id}`: Detalle de una licitación
- `GET /countries`: Lista de países disponibles
- `GET /sectors`: Lista de sectores disponibles

Ver documentación interactiva en `http://localhost:8000/docs`
