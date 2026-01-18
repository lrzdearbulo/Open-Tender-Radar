# Arquitectura de OpenTender Radar

Este documento describe las decisiones arquitectónicas y el diseño del core de OpenTender Radar.

## Principios de diseño

1. **Separación de responsabilidades**: El core de scoring está separado de la capa de presentación (API)
2. **Extensibilidad**: Fácil añadir nuevos adapters de datos sin modificar el core
3. **Explicabilidad**: El scoring es determinista y documentado
4. **Mantenibilidad**: Código limpio, bien estructurado, fácil de entender

## Capas de la aplicación

### 1. Capa de dominio (Core)

**Archivos**: `backend/models.py`, `backend/scoring.py`

Esta es la capa más importante y la que contiene el valor de negocio:

- **Models**: Define la estructura de datos de las licitaciones
- **ScoringEngine**: Implementa la lógica de scoring explicable

Esta capa es:
- Independiente del framework web
- Testeable de forma aislada
- Reutilizable en diferentes contextos
- El activo principal para licenciamiento

### 2. Capa de persistencia

**Archivo**: `backend/database.py`

- Configuración de SQLAlchemy
- Gestión de sesiones de base de datos
- Inicialización de esquema

**Diseño**: Usa SQLite por simplicidad, pero la arquitectura permite cambiar a PostgreSQL/MySQL sin modificar el core.

### 3. Capa de presentación (API)

**Archivo**: `backend/main.py`

- Endpoints FastAPI
- Validación de entrada (Pydantic)
- Orquestación de llamadas al core

**Diseño**: Esta capa es "delgada" - delega toda la lógica de negocio al core.

### 4. Capa de datos (Adapters futuros)

**Archivo**: `backend/seed.py` (actualmente solo mock)

En el futuro, esta capa incluirá adapters para:
- TED API
- Portales nacionales de contratación
- Otras fuentes de datos

**Diseño**: Los adapters normalizan datos externos al formato `TenderDB`, permitiendo que el core funcione sin cambios.

## Flujo de datos

```
Fuente de datos (TED, portal, etc.)
    ↓
Adapter (normaliza a TenderDB)
    ↓
ScoringEngine (calcula score)
    ↓
Persistencia (SQLite)
    ↓
API (expone resultados)
    ↓
Frontend (visualiza)
```

## Extensibilidad

### Añadir un nuevo adapter

1. Crear `backend/adapters/nuevo_adapter.py`
2. Implementar método que retorne lista de `TenderDB`
3. El resto del sistema funciona sin cambios

### Modificar el scoring

1. Editar `backend/scoring.py`
2. Modificar factores o añadir nuevos
3. El API y frontend se adaptan automáticamente

### Cambiar el framework web

1. El core (`scoring.py`, `models.py`) es independiente
2. Crear nueva capa de presentación (Flask, Django, etc.)
3. Reutilizar el core sin modificaciones

## Testing (futuro)

La arquitectura facilita testing:

- **Unit tests del core**: Testear `ScoringEngine` sin base de datos
- **Integration tests**: Testear flujo completo con datos mock
- **Adapter tests**: Testear normalización de datos externos

## Consideraciones de licenciamiento

La arquitectura está diseñada para permitir:

- Licenciar el core por separado
- Ofrecer diferentes niveles de funcionalidad
- Mantener el código fuente visible (Apache 2.0 + Commons Clause) pero proteger el uso comercial

El core (`scoring.py`, `models.py`) es el activo principal y está claramente separado de las capas de infraestructura.
