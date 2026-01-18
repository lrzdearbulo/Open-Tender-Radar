"""
API principal de OpenTender Radar.

FastAPI application que expone endpoints para consultar licitaciones
públicas con filtros y ordenación por score.

Este es el core de producto diseñado para ser extensible y licenciable.
La lógica de negocio (scoring) está separada en scoring.py para facilitar
la integración con adapters futuros y el licenciamiento comercial.

Licencia: Apache License 2.0 con Commons Clause License Condition v1.0
Para uso comercial, contacta: luisrzdearbulo@gmail.com
"""
from typing import Optional
from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from database import get_db, init_db
from models import TenderResponse, TenderListResponse, TenderStatus, TenderType
from models import TenderDB

# Inicializar FastAPI
app = FastAPI(
    title="OpenTender Radar API",
    description="API para consultar y filtrar licitaciones públicas con scoring de encaje",
    version="1.0.0"
)

# CORS middleware para permitir requests del frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Inicializa la base de datos al arrancar la aplicación."""
    init_db()


@app.get("/")
async def root():
    """Endpoint raíz con información básica de la API."""
    return {
        "name": "OpenTender Radar API",
        "version": "1.0.0",
        "description": "API para consultar licitaciones públicas con scoring de encaje"
    }


@app.get("/health")
async def health():
    """Endpoint de health check."""
    return {"status": "healthy"}


@app.get("/tenders", response_model=TenderListResponse)
async def get_tenders(
    country: Optional[str] = Query(None, description="Filtrar por código de país (ISO 3166-1 alpha-2)"),
    sector: Optional[str] = Query(None, description="Filtrar por sector"),
    status: Optional[TenderStatus] = Query(None, description="Filtrar por estado"),
    tender_type: Optional[TenderType] = Query(None, description="Filtrar por tipo de contrato"),
    min_score: Optional[float] = Query(None, ge=0, le=100, description="Score mínimo"),
    max_score: Optional[float] = Query(None, ge=0, le=100, description="Score máximo"),
    sort_by: str = Query("score", description="Campo por el que ordenar (score, budget, published_date)"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Orden de clasificación"),
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(20, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    """
    Obtiene una lista paginada de licitaciones con filtros opcionales.

    Permite filtrar por:
    - País
    - Sector
    - Estado
    - Tipo de contrato
    - Rango de score

    Permite ordenar por:
    - Score (por defecto, descendente)
    - Presupuesto
    - Fecha de publicación
    """
    # Construir query base
    query = db.query(TenderDB)
    
    # Aplicar filtros
    if country:
        query = query.filter(TenderDB.country == country.upper())
    if sector:
        query = query.filter(TenderDB.sector.ilike(f"%{sector}%"))
    if status:
        query = query.filter(TenderDB.status == status.value)
    if tender_type:
        query = query.filter(TenderDB.tender_type == tender_type.value)
    if min_score is not None:
        query = query.filter(TenderDB.score >= min_score)
    if max_score is not None:
        query = query.filter(TenderDB.score <= max_score)
    
    # Contar total (antes de paginación)
    total = query.count()
    
    # Aplicar ordenación
    if sort_by == "score":
        order_func = desc(TenderDB.score) if sort_order == "desc" else asc(TenderDB.score)
    elif sort_by == "budget":
        order_func = desc(TenderDB.budget) if sort_order == "desc" else asc(TenderDB.budget)
    elif sort_by == "published_date":
        order_func = desc(TenderDB.published_date) if sort_order == "desc" else asc(TenderDB.published_date)
    else:
        order_func = desc(TenderDB.score)  # Default
    
    query = query.order_by(order_func)
    
    # Aplicar paginación
    offset = (page - 1) * page_size
    tenders = query.offset(offset).limit(page_size).all()
    
    return TenderListResponse(
        items=[TenderResponse.model_validate(t) for t in tenders],
        total=total,
        page=page,
        page_size=page_size
    )


@app.get("/tenders/{tender_id}", response_model=TenderResponse)
async def get_tender(tender_id: int, db: Session = Depends(get_db)):
    """
    Obtiene una licitación específica por ID.
    """
    tender = db.query(TenderDB).filter(TenderDB.id == tender_id).first()
    if not tender:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Tender not found")
    return TenderResponse.model_validate(tender)


@app.get("/countries")
async def get_countries(db: Session = Depends(get_db)):
    """
    Obtiene la lista de países únicos disponibles en la base de datos.
    """
    countries = db.query(TenderDB.country).distinct().all()
    return {"countries": [c[0] for c in countries]}


@app.get("/sectors")
async def get_sectors(db: Session = Depends(get_db)):
    """
    Obtiene la lista de sectores únicos disponibles en la base de datos.
    """
    sectors = db.query(TenderDB.sector).distinct().all()
    return {"sectors": [s[0] for s in sectors]}
