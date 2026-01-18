"""
Modelos de datos para OpenTender Radar.

Define los modelos Pydantic para validación y los modelos SQLAlchemy
para persistencia en base de datos.
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy import Column, Float, Integer, String, Text, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class TenderStatus(str, Enum):
    """Estados posibles de una licitación."""
    OPEN = "open"
    CLOSED = "closed"
    AWARDED = "awarded"
    CANCELLED = "cancelled"


class TenderType(str, Enum):
    """Tipos de contrato."""
    WORKS = "works"
    SUPPLIES = "supplies"
    SERVICES = "services"
    CONCESSION = "concession"


# Modelo SQLAlchemy para base de datos
class TenderDB(Base):
    """Modelo de base de datos para licitaciones."""
    __tablename__ = "tenders"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text)
    country = Column(String, nullable=False, index=True)
    sector = Column(String, nullable=False, index=True)
    cpv_code = Column(String, index=True)  # Código CPV (Common Procurement Vocabulary)
    budget = Column(Float)
    currency = Column(String, default="EUR")
    status = Column(String, default=TenderStatus.OPEN.value)
    tender_type = Column(String)
    deadline = Column(DateTime)
    published_date = Column(DateTime, default=datetime.utcnow)
    keywords = Column(Text)  # Palabras clave separadas por comas
    score = Column(Float, index=True)  # Score calculado (0-100)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Modelos Pydantic para API
class TenderBase(BaseModel):
    """Modelo base para licitaciones."""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    country: str = Field(..., min_length=2, max_length=3)
    sector: str = Field(..., min_length=1, max_length=100)
    cpv_code: Optional[str] = None
    budget: Optional[float] = Field(None, gt=0)
    currency: str = Field(default="EUR", max_length=3)
    status: TenderStatus = TenderStatus.OPEN
    tender_type: Optional[TenderType] = None
    deadline: Optional[datetime] = None
    published_date: Optional[datetime] = None
    keywords: Optional[str] = None


class TenderCreate(TenderBase):
    """Modelo para crear una licitación."""
    pass


class TenderResponse(TenderBase):
    """Modelo de respuesta para licitaciones."""
    id: int
    score: float = Field(..., ge=0, le=100)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TenderListResponse(BaseModel):
    """Respuesta paginada de licitaciones."""
    items: list[TenderResponse]
    total: int
    page: int
    page_size: int
