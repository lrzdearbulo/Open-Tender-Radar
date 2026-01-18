"""
Configuración y gestión de la base de datos.

Maneja la conexión a SQLite y proporciona utilidades para
inicializar y gestionar la base de datos.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base

# Ruta a la base de datos SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./opentender.db")

# Motor de base de datos
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Inicializa la base de datos creando todas las tablas."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    Dependency para FastAPI que proporciona una sesión de base de datos.

    Yields:
        Session: Sesión de SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
