# OpenTender Radar

Core de análisis de licitaciones públicas con scoring explicable de encaje de negocio.

## El problema

Las empresas que compiten en licitaciones públicas enfrentan un problema de señal-ruido: hay demasiada información dispersa y es difícil identificar qué oportunidades realmente encajan con su perfil de negocio, capacidades y estrategia.

OpenTender Radar normaliza datos de licitaciones y calcula un score determinista (0-100) que indica el encaje de cada oportunidad. El scoring es **explicable**: cada punto tiene una razón clara basada en reglas objetivas, no en modelos de caja negra.

## El enfoque

Este proyecto es un **core de producto**, no un experimento técnico. La arquitectura está pensada para ser:

- **Extensible**: Separación clara entre core de scoring y posibles adapters futuros (TED API, portales nacionales, etc.)
- **Explicable**: El scoring es determinista y documentado, no una caja negra
- **Mantenible**: Código limpio, bien estructurado, con decisiones arquitectónicas explícitas
- **Licenciable**: Diseñado como activo estratégico con modelo de licencia claro

**Filosofía técnica:**
- Scoring basado en reglas > ML complejo (para este caso de uso)
- Código legible > Optimización prematura
- Arquitectura modular > Monolito acoplado
- Documentación con sentido > Documentación exhaustiva

## Cómo funciona el scoring

El sistema calcula un score de 0-100 mediante factores ponderados y documentados. Cada factor aporta puntos según criterios objetivos.

### Factores de scoring

1. **Presupuesto (0-30 puntos)**
   - < 10k: 0 puntos
   - 10k-50k: 5 puntos
   - 50k-100k: 15 puntos
   - 100k-500k: 25 puntos
   - > 500k: 30 puntos

2. **País prioritario (0-20 puntos)**
   - País en lista de prioridades: 20 puntos
   - Otro país: 5 puntos

3. **Sector objetivo (0-20 puntos)**
   - Sector alineado con objetivos: 20 puntos
   - Otro sector: 5 puntos

4. **Palabras clave relevantes (0-15 puntos)**
   - 0 coincidencias: 0 puntos
   - 1-2 coincidencias: 5 puntos
   - 3-4 coincidencias: 10 puntos
   - 5+ coincidencias: 15 puntos

5. **Tipo de contrato (0-10 puntos, puede ser negativo)**
   - SERVICES o SUPPLIES: 10 puntos
   - WORKS o CONCESSION: -5 puntos (penalización)

6. **Estado (0-5 puntos)**
   - OPEN: 5 puntos
   - Otros estados: 0 puntos

El score final es la suma de todos los factores, limitado entre 0 y 100.

**¿Por qué este enfoque?**
- **Determinista**: Misma licitación = mismo score, siempre
- **Explicable**: Puedes ver exactamente por qué una licitación tiene X puntos
- **Modificable**: Cambiar las reglas es editar `scoring.py`, no retrenar modelos
- **Sin dependencias**: No requiere datos históricos ni entrenamiento

La lógica completa está en `backend/scoring.py`, documentada y lista para personalización.

## Arquitectura

```
opentender-radar/
├── backend/              # Core de análisis
│   ├── main.py          # API FastAPI (capa de presentación)
│   ├── models.py        # Modelos de dominio (Pydantic + SQLAlchemy)
│   ├── database.py      # Configuración de persistencia
│   ├── scoring.py       # Motor de scoring (core del negocio)
│   └── seed.py          # Datos simulados (TED-like)
├── frontend/            # Dashboard de visualización
│   └── src/
│       ├── App.jsx
│       └── components/
│           └── TenderTable.jsx
└── docker-compose.yml
```

**Separación de responsabilidades:**
- `scoring.py`: Lógica de negocio pura, independiente del framework
- `models.py`: Modelos de dominio y validación
- `main.py`: Endpoints HTTP, orquestación
- `seed.py`: Simulación de fuentes de datos reales

Esta arquitectura facilita:
- Añadir nuevos adapters de datos (TED, portales nacionales)
- Cambiar el framework web sin tocar el core
- Testear el scoring de forma aislada
- Licenciar componentes por separado si es necesario

## Datos

Este proyecto usa **datos simulados** que imitan la estructura de fuentes reales (TED, portales de contratación pública). Los datos mock están en `backend/seed.py` y generan 50 licitaciones con:

- Estructura similar a TED (CPV codes, países, sectores)
- Variedad realista de presupuestos, estados y tipos
- Palabras clave relevantes para scoring

**Para producción:** El core está diseñado para integrarse con adapters que consuman APIs reales. La estructura de datos es compatible con formatos estándar de licitaciones públicas.

## Instalación y uso

### Prerrequisitos

- Python 3.11+
- Node.js 18+
- Docker y Docker Compose (recomendado)

### Opción 1: Docker Compose (recomendado)

```bash
# Construir e iniciar servicios
docker-compose up --build -d

# Poblar base de datos con datos simulados
docker-compose exec backend python seed.py

# Ver logs
docker-compose logs -f
```

- Frontend: `http://localhost:5173`
- API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

### Opción 2: Desarrollo local

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed.py
uvicorn main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API

### Endpoints principales

**Lista de licitaciones (con filtros y paginación):**
```bash
GET /tenders?country=ES&sector=technology&sort_by=score&sort_order=desc&page=1&page_size=20
```

**Detalle de licitación:**
```bash
GET /tenders/{id}
```

**Países disponibles:**
```bash
GET /countries
```

**Sectores disponibles:**
```bash
GET /sectors
```

Ver documentación interactiva completa en `http://localhost:8000/docs`

## Personalización

### Ajustar el scoring

Edita `backend/scoring.py`. La clase `ScoringEngine` está diseñada para ser modificable:

```python
# Cambiar países prioritarios
PRIORITY_COUNTRIES = ["ES", "PT", "FR", ...]

# Cambiar sectores objetivo
TARGET_SECTORS = ["technology", "software", ...]

# Cambiar palabras clave relevantes
RELEVANT_KEYWORDS = ["digital", "cloud", ...]

# Modificar lógica de cada factor
def _score_budget(self, budget, currency):
    # Tu lógica personalizada
```

### Integrar fuentes reales

El core está preparado para adapters. Ejemplo de estructura:

```python
# backend/adapters/ted_adapter.py (futuro)
class TEDAdapter:
    def fetch_tenders(self):
        # Consumir TED API
        # Normalizar a formato TenderDB
        pass
```

## Roadmap (no implementado)

Estas son mejoras potenciales que **no están en el MVP actual**:

- **Adapters de datos reales**: Integración con TED API, portales nacionales
- **Notificaciones**: Alertas cuando aparecen licitaciones con score alto
- **Exportación**: CSV/Excel de resultados
- **Histórico**: Tracking de cambios en licitaciones
- **Multi-perfil**: Diferentes configuraciones de scoring por perfil de negocio
- **Webhooks**: Notificar sistemas externos de nuevas oportunidades
- **Análisis de tendencias**: Evolución de oportunidades por sector/país
- **API de scoring**: Endpoint para calcular score de licitaciones externas

## Licencia

Este proyecto está licenciado bajo **Apache License 2.0 con Commons Clause License Condition v1.0**.

### ¿Qué significa esto?

**Puedes:**
- Ver el código fuente completo
- Usar el proyecto para evaluación técnica
- Usar el proyecto para aprendizaje y educación
- Usar el proyecto para proyectos personales no comerciales
- Modificar el código para tus necesidades (dentro de las restricciones)
- Redistribuir el código (con atribución y NOTICE)

**NO puedes:**
- Usar el proyecto para fines comerciales
- Usar el proyecto para operaciones internas de negocio
- Ofrecer el proyecto como SaaS (Software as a Service)
- Ofrecer el proyecto como servicio hospedado
- Integrar el proyecto en productos o servicios de pago
- Vender productos o servicios cuyo valor derive sustancialmente del Software

### Licencias comerciales

Si necesitas usar OpenTender Radar para:
- Operaciones comerciales
- Uso interno empresarial
- Integración en productos comerciales
- Ofrecer como servicio hospedado o SaaS
- Cualquier uso que implique monetización

Por favor, contacta para licencias comerciales: **luisrzdearbulo@gmail.com**

### ¿Por qué esta licencia?

OpenTender Radar es un activo estratégico diseñado para ser licenciado comercialmente. Apache 2.0 + Commons Clause permite:
- **Transparencia**: El código es visible y auditable
- **Protección comercial**: El valor comercial está protegido mediante Commons Clause
- **Flexibilidad**: Modelo de licenciamiento claro para casos de uso comerciales
- **Estándar**: Apache 2.0 es una licencia ampliamente reconocida y aceptada

**Nota importante**: Esta combinación de licencias (Apache 2.0 + Commons Clause) no es reconocida como "open source" por la Open Source Initiative (OSI) debido a las restricciones comerciales. Es una licencia de "source available" (código disponible) con restricciones comerciales.

## Contribuciones

Este proyecto acepta contribuciones bajo los términos de la licencia. Al contribuir, aceptas que tus contribuciones serán licenciadas bajo Apache License 2.0 con Commons Clause License Condition v1.0.

Para contribuir:
1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Soporte

- **Issues**: Para bugs y feature requests, usa GitHub Issues
- **Licencias comerciales**: luisrzdearbulo@gmail.com
- **Preguntas técnicas**: Abre una discusión en GitHub

---

**OpenTender Radar** - Core de análisis de licitaciones públicas. Diseñado como activo estratégico, construido con código limpio.
