"""
Motor de scoring para licitaciones.

Este es el CORE del negocio: implementa un sistema de scoring explicable
basado en reglas claras. El score final va de 0 a 100 y se calcula mediante
factores ponderados.

Cada factor aporta puntos positivos o negativos según criterios
objetivos y documentados. El scoring es determinista y explicable.

ARQUITECTURA:
Este módulo está diseñado para ser independiente del framework web,
facilitando su reutilización, testing y posible licenciamiento por separado.

Licencia: Apache License 2.0 con Commons Clause License Condition v1.0
Para uso comercial, contacta: luisrzdearbulo@gmail.com
"""
from datetime import datetime
from typing import Optional

from models import TenderDB, TenderType


class ScoringEngine:
    """
    Motor de scoring para licitaciones públicas.

    Calcula un score de 0-100 basado en:
    - Presupuesto (mayor presupuesto = más puntos)
    - País prioritario (configurable)
    - CPV code (alineación con sectores objetivo)
    - Palabras clave relevantes
    - Tipo de contrato (algunos tipos son más relevantes)
    - Estado de la licitación (abiertas tienen más valor)
    - Antigüedad (licitaciones recientes valen más)

    El scoring es determinista y explicable: cada punto tiene
    una razón clara y documentada.
    """

    # Configuración de países prioritarios (puede venir de env o config)
    PRIORITY_COUNTRIES = ["ES", "PT", "FR", "IT", "DE", "UK"]
    
    # Sectores objetivo (puede venir de config)
    TARGET_SECTORS = [
        "technology",
        "software",
        "consulting",
        "digital",
        "it",
        "telecommunications"
    ]
    
    # Palabras clave relevantes (puede venir de config)
    RELEVANT_KEYWORDS = [
        "digital",
        "software",
        "cloud",
        "api",
        "saas",
        "platform",
        "data",
        "analytics",
        "ai",
        "machine learning",
        "blockchain",
        "cybersecurity"
    ]
    
    # Tipos de contrato con penalización (menos relevantes)
    LESS_RELEVANT_TYPES = [TenderType.WORKS, TenderType.CONCESSION]

    def __init__(
        self,
        priority_countries: Optional[list[str]] = None,
        target_sectors: Optional[list[str]] = None,
        relevant_keywords: Optional[list[str]] = None
    ):
        """
        Inicializa el motor de scoring.

        Args:
            priority_countries: Lista de códigos de países prioritarios
            target_sectors: Lista de sectores objetivo
            relevant_keywords: Lista de palabras clave relevantes
        """
        if priority_countries:
            self.PRIORITY_COUNTRIES = priority_countries
        if target_sectors:
            self.TARGET_SECTORS = target_sectors
        if relevant_keywords:
            self.RELEVANT_KEYWORDS = relevant_keywords

    def calculate_score(self, tender: TenderDB) -> float:
        """
        Calcula el score de una licitación.

        Args:
            tender: Objeto TenderDB con los datos de la licitación

        Returns:
            float: Score entre 0 y 100
        """
        score = 0.0
        
        # Factor 1: Presupuesto (0-30 puntos)
        # Presupuestos mayores a 100k EUR reciben puntos proporcionales
        score += self._score_budget(tender.budget, tender.currency)
        
        # Factor 2: País prioritario (0-20 puntos)
        score += self._score_country(tender.country)
        
        # Factor 3: Sector objetivo (0-20 puntos)
        score += self._score_sector(tender.sector)
        
        # Factor 4: Palabras clave (0-15 puntos)
        score += self._score_keywords(tender.keywords, tender.description)
        
        # Factor 5: Tipo de contrato (0-10 puntos, puede ser negativo)
        score += self._score_tender_type(tender.tender_type)
        
        # Factor 6: Estado (0-5 puntos)
        score += self._score_status(tender.status)
        
        # Asegurar que el score esté entre 0 y 100
        return max(0.0, min(100.0, score))

    def _score_budget(self, budget: Optional[float], currency: str) -> float:
        """
        Calcula puntos basados en el presupuesto.

        Lógica:
        - < 10k: 0 puntos
        - 10k-50k: 5 puntos
        - 50k-100k: 15 puntos
        - 100k-500k: 25 puntos
        - > 500k: 30 puntos

        Args:
            budget: Presupuesto en la moneda especificada
            currency: Código de moneda (asumimos EUR para simplificar)

        Returns:
            float: Puntos por presupuesto (0-30)
        """
        if not budget:
            return 0.0
        
        # Normalización básica (asumimos EUR, en producción usar conversión real)
        if budget < 10000:
            return 0.0
        elif budget < 50000:
            return 5.0
        elif budget < 100000:
            return 15.0
        elif budget < 500000:
            return 25.0
        else:
            return 30.0

    def _score_country(self, country: str) -> float:
        """
        Calcula puntos basados en el país.

        Lógica:
        - País prioritario: 20 puntos
        - Otro país: 5 puntos

        Args:
            country: Código de país (ISO 3166-1 alpha-2)

        Returns:
            float: Puntos por país (0-20)
        """
        if country.upper() in [c.upper() for c in self.PRIORITY_COUNTRIES]:
            return 20.0
        return 5.0

    def _score_sector(self, sector: str) -> float:
        """
        Calcula puntos basados en el sector.

        Lógica:
        - Sector objetivo: 20 puntos
        - Otro sector: 5 puntos

        Args:
            sector: Nombre del sector

        Returns:
            float: Puntos por sector (0-20)
        """
        if not sector:
            return 0.0
        
        sector_lower = sector.lower()
        for target in self.TARGET_SECTORS:
            if target in sector_lower:
                return 20.0
        return 5.0

    def _score_keywords(self, keywords: Optional[str], description: Optional[str]) -> float:
        """
        Calcula puntos basados en palabras clave relevantes.

        Lógica:
        - 0 coincidencias: 0 puntos
        - 1-2 coincidencias: 5 puntos
        - 3-4 coincidencias: 10 puntos
        - 5+ coincidencias: 15 puntos

        Args:
            keywords: Palabras clave separadas por comas
            description: Descripción de la licitación

        Returns:
            float: Puntos por palabras clave (0-15)
        """
        text = ""
        if keywords:
            text += keywords.lower() + " "
        if description:
            text += description.lower() + " "
        
        if not text:
            return 0.0
        
        matches = 0
        for keyword in self.RELEVANT_KEYWORDS:
            if keyword.lower() in text:
                matches += 1
        
        if matches == 0:
            return 0.0
        elif matches <= 2:
            return 5.0
        elif matches <= 4:
            return 10.0
        else:
            return 15.0

    def _score_tender_type(self, tender_type: Optional[TenderType]) -> float:
        """
        Calcula puntos basados en el tipo de contrato.

        Lógica:
        - SERVICES o SUPPLIES: 10 puntos
        - WORKS o CONCESSION: -5 puntos (penalización)
        - Sin tipo: 0 puntos

        Args:
            tender_type: Tipo de contrato

        Returns:
            float: Puntos por tipo (-5 a 10)
        """
        if not tender_type:
            return 0.0
        
        if tender_type in self.LESS_RELEVANT_TYPES:
            return -5.0
        elif tender_type in [TenderType.SERVICES, TenderType.SUPPLIES]:
            return 10.0
        
        return 0.0

    def _score_status(self, status: str) -> float:
        """
        Calcula puntos basados en el estado de la licitación.

        Lógica:
        - OPEN: 5 puntos
        - Otros estados: 0 puntos

        Args:
            status: Estado de la licitación

        Returns:
            float: Puntos por estado (0-5)
        """
        if status == "open":
            return 5.0
        return 0.0

    def explain_score(self, tender: TenderDB) -> dict:
        """
        Explica el cálculo del score desglosando cada factor.

        Útil para debugging y transparencia.

        Args:
            tender: Objeto TenderDB

        Returns:
            dict: Desglose del score por factores
        """
        return {
            "total": self.calculate_score(tender),
            "breakdown": {
                "budget": self._score_budget(tender.budget, tender.currency),
                "country": self._score_country(tender.country),
                "sector": self._score_sector(tender.sector),
                "keywords": self._score_keywords(tender.keywords, tender.description),
                "tender_type": self._score_tender_type(tender.tender_type),
                "status": self._score_status(tender.status)
            }
        }
