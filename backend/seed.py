"""
Script de seed para poblar la base de datos con datos simulados.

Genera licitaciones mock que imitan la estructura de fuentes reales
(TED, portales de contratación pública) para desarrollo y demostración.

NOTA: Estos son datos simulados. Para producción, el core está diseñado
para integrarse con adapters que consuman APIs reales de licitaciones públicas.

Licencia: Apache License 2.0 con Commons Clause License Condition v1.0
Para uso comercial, contacta: luisrzdearbulo@gmail.com
"""
from datetime import datetime, timedelta
import random

from database import SessionLocal, init_db
from models import TenderDB, TenderStatus, TenderType
from scoring import ScoringEngine


def generate_mock_tenders() -> list[dict]:
    """
    Genera una lista de licitaciones mock.

    Returns:
        list[dict]: Lista de diccionarios con datos de licitaciones
    """
    countries = ["ES", "PT", "FR", "IT", "DE", "UK", "NL", "BE", "PL", "SE"]
    sectors = [
        "technology",
        "software development",
        "digital transformation",
        "consulting services",
        "it infrastructure",
        "telecommunications",
        "construction",
        "healthcare",
        "education",
        "public administration"
    ]
    
    tender_titles = [
        "Digital Platform for Public Services",
        "Cloud Infrastructure Migration",
        "Cybersecurity Assessment Services",
        "API Development and Integration",
        "Data Analytics Platform",
        "Software Development Framework",
        "Machine Learning Solutions",
        "Blockchain Implementation",
        "SaaS Platform Development",
        "IT Consulting Services",
        "Road Construction Project",
        "Building Maintenance Services",
        "Medical Equipment Supply",
        "Educational Software Platform",
        "Telecommunications Network Upgrade"
    ]
    
    descriptions = [
        "Development of a comprehensive digital platform to modernize public services and improve citizen engagement.",
        "Migration of legacy systems to cloud infrastructure with focus on scalability and security.",
        "Comprehensive cybersecurity assessment and implementation of security best practices.",
        "Development and integration of RESTful APIs for inter-system communication.",
        "Implementation of a data analytics platform for business intelligence and reporting.",
        "Framework development for scalable software solutions.",
        "Implementation of machine learning models for predictive analytics.",
        "Blockchain-based solution for secure document management.",
        "Development of a Software-as-a-Service platform for enterprise clients.",
        "IT consulting services for digital transformation initiatives.",
        "Construction of new road infrastructure connecting major cities.",
        "Maintenance and repair services for public buildings.",
        "Supply of medical equipment for public hospitals.",
        "Educational software platform for online learning.",
        "Upgrade of telecommunications network infrastructure."
    ]
    
    keywords_list = [
        "digital, cloud, api, saas, platform",
        "cloud, infrastructure, migration, scalability",
        "cybersecurity, security, assessment, compliance",
        "api, development, integration, restful",
        "data, analytics, business intelligence, reporting",
        "software, development, framework, scalable",
        "ai, machine learning, predictive analytics",
        "blockchain, secure, document management",
        "saas, platform, enterprise, cloud",
        "consulting, digital transformation, it",
        "construction, infrastructure, roads",
        "maintenance, repair, buildings",
        "medical, equipment, healthcare, supply",
        "education, software, online learning",
        "telecommunications, network, infrastructure"
    ]
    
    cpv_codes = [
        "48000000",  # Software package and information systems
        "72000000",  # IT services
        "48000000",  # Software
        "72000000",  # IT services
        "48000000",  # Software
        "48000000",  # Software
        "48000000",  # Software
        "48000000",  # Software
        "48000000",  # Software
        "72000000",  # IT services
        "45000000",  # Construction work
        "50000000",  # Repair and maintenance services
        "33000000",  # Medical equipment
        "48000000",  # Software
        "32000000"   # Radio, television, communication equipment
    ]
    
    tenders = []
    base_date = datetime.utcnow()
    
    for i in range(50):  # Generamos 50 licitaciones
        # Seleccionamos datos aleatorios pero coherentes
        idx = i % len(tender_titles)
        
        # Presupuesto aleatorio entre 5k y 1M
        budget = random.uniform(5000, 1000000)
        
        # Fecha de publicación (últimos 90 días)
        days_ago = random.randint(0, 90)
        published_date = base_date - timedelta(days=days_ago)
        
        # Deadline (entre hoy y 60 días)
        days_ahead = random.randint(1, 60)
        deadline = base_date + timedelta(days=days_ahead)
        
        # Estado (mayoría abiertas)
        status = random.choices(
            [TenderStatus.OPEN, TenderStatus.CLOSED, TenderStatus.AWARDED],
            weights=[70, 20, 10]
        )[0]
        
        # Tipo de contrato
        tender_type = random.choice(list(TenderType))
        
        tender_data = {
            "title": tender_titles[idx],
            "description": descriptions[idx],
            "country": random.choice(countries),
            "sector": random.choice(sectors),
            "cpv_code": cpv_codes[idx],
            "budget": round(budget, 2),
            "currency": "EUR",
            "status": status.value,
            "tender_type": tender_type.value,
            "deadline": deadline,
            "published_date": published_date,
            "keywords": keywords_list[idx]
        }
        
        tenders.append(tender_data)
    
    return tenders


def seed_database():
    """
    Pobla la base de datos con licitaciones mock.

    Calcula el score para cada licitación antes de guardarla.
    """
    print("Inicializando base de datos...")
    init_db()
    
    print("Generando datos mock...")
    mock_tenders = generate_mock_tenders()
    
    print("Calculando scores y guardando licitaciones...")
    db = SessionLocal()
    scoring_engine = ScoringEngine()
    
    try:
        # Limpiar datos existentes (opcional, para desarrollo)
        db.query(TenderDB).delete()
        db.commit()
        
        for tender_data in mock_tenders:
            # Crear objeto TenderDB
            tender = TenderDB(**tender_data)
            
            # Calcular score
            tender.score = scoring_engine.calculate_score(tender)
            
            # Guardar en base de datos
            db.add(tender)
        
        db.commit()
        print(f"✅ Se han creado {len(mock_tenders)} licitaciones con scores calculados.")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error al poblar la base de datos: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
