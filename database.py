import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, JSON, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Dict, Any, Optional, List

DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL) if DATABASE_URL else None
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None
Base = declarative_base()


class AnalysisRecord(Base):
    __tablename__ = "analysis_records"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    business_name = Column(String(255), nullable=True)
    business_type = Column(String(100))
    num_outlets = Column(Integer)
    total_land_sqft = Column(Float)
    region = Column(String(100))
    state = Column(String(100), nullable=True)
    land_rate_per_sqft = Column(Float)
    electricity_consumption_kwh = Column(Float)
    declared_revenue = Column(Float)
    declared_tax_paid = Column(Float)
    num_employees = Column(Integer)
    is_stock_listed = Column(Boolean)
    stock_market_cap = Column(Float, default=0)
    tycoon_connection_level = Column(String(100))
    years_in_operation = Column(Integer)
    additional_notes = Column(Text, nullable=True)
    
    fraud_probability = Column(Float)
    risk_level = Column(String(50))
    ml_score = Column(Float)
    recommendation = Column(Text)
    risk_factors = Column(JSON)
    anomaly_scores = Column(JSON)
    detailed_analysis = Column(JSON)
    matched_fraud_patterns = Column(JSON, nullable=True)
    
    business_address = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    satellite_measured_area = Column(Float, nullable=True)
    area_discrepancy_percent = Column(Float, nullable=True)
    satellite_image_url = Column(Text, nullable=True)
    
    is_small_vendor = Column(Boolean, default=False)
    lifestyle_analysis = Column(JSON, nullable=True)
    visual_analysis = Column(JSON, nullable=True)
    network_analysis = Column(JSON, nullable=True)


class VendorAnalysis(Base):
    __tablename__ = "vendor_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    analysis_id = Column(Integer, nullable=True)
    
    vendor_name = Column(String(255))
    vendor_type = Column(String(100))
    location_description = Column(Text, nullable=True)
    
    stall_photo_data = Column(LargeBinary, nullable=True)
    visual_analysis_result = Column(JSON, nullable=True)
    
    estimated_daily_revenue = Column(Float, nullable=True)
    declared_monthly_revenue = Column(Float, nullable=True)
    revenue_discrepancy = Column(Float, nullable=True)
    
    lifestyle_indicators = Column(JSON, nullable=True)
    lifestyle_risk_score = Column(Float, nullable=True)
    
    network_connections = Column(JSON, nullable=True)
    network_risk_score = Column(Float, nullable=True)
    
    overall_fraud_score = Column(Float, nullable=True)
    risk_level = Column(String(50), nullable=True)
    field_officer_notes = Column(Text, nullable=True)


class FraudPattern(Base):
    __tablename__ = "fraud_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    pattern_name = Column(String(255))
    pattern_type = Column(String(100))
    description = Column(Text)
    key_indicators = Column(JSON)
    detection_rules = Column(JSON)
    risk_weight = Column(Float, default=0.5)
    source = Column(String(255), nullable=True)
    source_url = Column(Text, nullable=True)
    case_reference = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)


class NewsArticle(Base):
    __tablename__ = "news_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    title = Column(String(500))
    url = Column(Text, unique=True)
    source = Column(String(255))
    published_date = Column(DateTime, nullable=True)
    content = Column(Text)
    summary = Column(Text, nullable=True)
    
    extracted_patterns = Column(JSON, nullable=True)
    fraud_types_mentioned = Column(JSON, nullable=True)
    entities_mentioned = Column(JSON, nullable=True)
    amount_mentioned = Column(Float, nullable=True)
    is_processed = Column(Boolean, default=False)


class LocationData(Base):
    __tablename__ = "location_data"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    analysis_id = Column(Integer, nullable=True)
    business_name = Column(String(255))
    address = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    place_id = Column(String(255), nullable=True)
    
    declared_area_sqft = Column(Float, nullable=True)
    measured_area_sqft = Column(Float, nullable=True)
    area_discrepancy = Column(Float, nullable=True)
    
    polygon_coordinates = Column(JSON, nullable=True)
    satellite_image_data = Column(LargeBinary, nullable=True)
    verification_status = Column(String(50), default="pending")


class NetworkEntity(Base):
    __tablename__ = "network_entities"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    entity_id = Column(String(100), unique=True)
    entity_type = Column(String(50))
    name = Column(String(255))
    risk_score = Column(Float, default=0)
    
    entity_metadata = Column(JSON, nullable=True)


class NetworkConnection(Base):
    __tablename__ = "network_connections"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    from_entity_id = Column(String(100))
    to_entity_id = Column(String(100))
    connection_type = Column(String(50))
    strength = Column(Float, default=0.5)
    connection_metadata = Column(JSON, nullable=True)


class FieldInvestigation(Base):
    __tablename__ = "field_investigations"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    analysis_id = Column(Integer, nullable=True)
    vendor_analysis_id = Column(Integer, nullable=True)
    
    officer_name = Column(String(255))
    officer_id = Column(String(100))
    
    investigation_status = Column(String(50), default="pending")
    priority = Column(String(50), default="normal")
    
    location = Column(Text, nullable=True)
    gps_coordinates = Column(JSON, nullable=True)
    
    photos = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)
    findings = Column(JSON, nullable=True)
    
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime, nullable=True)


def init_db():
    if engine:
        Base.metadata.create_all(bind=engine)
        return True
    return False


def get_db_session():
    if SessionLocal:
        return SessionLocal()
    return None


def save_analysis_result(business_data: Dict[str, Any], result: Dict[str, Any], business_name: Optional[str] = None) -> Optional[int]:
    session = get_db_session()
    if not session:
        return None
    
    try:
        record = AnalysisRecord(
            business_name=business_name,
            business_type=business_data.get("business_type"),
            num_outlets=business_data.get("num_outlets"),
            total_land_sqft=business_data.get("total_land_sqft"),
            region=business_data.get("region"),
            state=business_data.get("state"),
            land_rate_per_sqft=business_data.get("land_rate_per_sqft"),
            electricity_consumption_kwh=business_data.get("electricity_consumption_kwh"),
            declared_revenue=business_data.get("declared_revenue"),
            declared_tax_paid=business_data.get("declared_tax_paid"),
            num_employees=business_data.get("num_employees"),
            is_stock_listed=business_data.get("is_stock_listed", False),
            stock_market_cap=business_data.get("stock_market_cap", 0),
            tycoon_connection_level=business_data.get("tycoon_connection_level"),
            years_in_operation=business_data.get("years_in_operation"),
            additional_notes=business_data.get("additional_notes"),
            fraud_probability=result.get("fraud_probability"),
            risk_level=result.get("risk_level"),
            ml_score=result.get("ml_score"),
            recommendation=result.get("recommendation"),
            risk_factors=result.get("risk_factors"),
            anomaly_scores=result.get("anomaly_scores"),
            detailed_analysis=result.get("detailed_analysis"),
            matched_fraud_patterns=result.get("matched_fraud_patterns"),
            business_address=business_data.get("business_address"),
            latitude=business_data.get("latitude"),
            longitude=business_data.get("longitude"),
            satellite_measured_area=business_data.get("satellite_measured_area"),
            area_discrepancy_percent=business_data.get("area_discrepancy_percent"),
            is_small_vendor=result.get("is_small_vendor", False),
            lifestyle_analysis=business_data.get("lifestyle_analysis"),
            visual_analysis=business_data.get("visual_analysis"),
            network_analysis=business_data.get("network_analysis")
        )
        
        session.add(record)
        session.commit()
        record_id = int(record.id)
        session.close()
        return record_id
    except Exception as e:
        session.rollback()
        session.close()
        print(f"Error saving analysis: {e}")
        return None


def save_vendor_analysis(vendor_data: Dict) -> Optional[int]:
    session = get_db_session()
    if not session:
        return None
    
    try:
        record = VendorAnalysis(
            analysis_id=vendor_data.get("analysis_id"),
            vendor_name=vendor_data.get("vendor_name"),
            vendor_type=vendor_data.get("vendor_type"),
            location_description=vendor_data.get("location_description"),
            visual_analysis_result=vendor_data.get("visual_analysis_result"),
            estimated_daily_revenue=vendor_data.get("estimated_daily_revenue"),
            declared_monthly_revenue=vendor_data.get("declared_monthly_revenue"),
            revenue_discrepancy=vendor_data.get("revenue_discrepancy"),
            lifestyle_indicators=vendor_data.get("lifestyle_indicators"),
            lifestyle_risk_score=vendor_data.get("lifestyle_risk_score"),
            network_connections=vendor_data.get("network_connections"),
            network_risk_score=vendor_data.get("network_risk_score"),
            overall_fraud_score=vendor_data.get("overall_fraud_score"),
            risk_level=vendor_data.get("risk_level"),
            field_officer_notes=vendor_data.get("field_officer_notes")
        )
        
        session.add(record)
        session.commit()
        record_id = int(record.id)
        session.close()
        return record_id
    except Exception as e:
        session.rollback()
        session.close()
        print(f"Error saving vendor analysis: {e}")
        return None


def get_all_analysis_records() -> List[Dict]:
    session = get_db_session()
    if not session:
        return []
    
    try:
        records = session.query(AnalysisRecord).order_by(AnalysisRecord.created_at.desc()).all()
        results = []
        for r in records:
            results.append({
                "id": r.id,
                "created_at": r.created_at,
                "business_name": r.business_name,
                "business_type": r.business_type,
                "num_outlets": r.num_outlets,
                "declared_revenue": r.declared_revenue,
                "fraud_probability": r.fraud_probability,
                "risk_level": r.risk_level,
                "ml_score": r.ml_score,
                "recommendation": r.recommendation,
                "state": r.state,
                "is_small_vendor": r.is_small_vendor
            })
        session.close()
        return results
    except Exception as e:
        session.close()
        print(f"Error fetching records: {e}")
        return []


def get_analysis_by_id(record_id: int) -> Optional[Dict]:
    session = get_db_session()
    if not session:
        return None
    
    try:
        record = session.query(AnalysisRecord).filter(AnalysisRecord.id == record_id).first()
        if record:
            result = {
                "id": record.id,
                "created_at": record.created_at,
                "business_name": record.business_name,
                "business_type": record.business_type,
                "num_outlets": record.num_outlets,
                "total_land_sqft": record.total_land_sqft,
                "region": record.region,
                "state": record.state,
                "land_rate_per_sqft": record.land_rate_per_sqft,
                "electricity_consumption_kwh": record.electricity_consumption_kwh,
                "declared_revenue": record.declared_revenue,
                "declared_tax_paid": record.declared_tax_paid,
                "num_employees": record.num_employees,
                "is_stock_listed": record.is_stock_listed,
                "stock_market_cap": record.stock_market_cap,
                "tycoon_connection_level": record.tycoon_connection_level,
                "years_in_operation": record.years_in_operation,
                "additional_notes": record.additional_notes,
                "fraud_probability": record.fraud_probability,
                "risk_level": record.risk_level,
                "ml_score": record.ml_score,
                "recommendation": record.recommendation,
                "risk_factors": record.risk_factors,
                "anomaly_scores": record.anomaly_scores,
                "detailed_analysis": record.detailed_analysis,
                "matched_fraud_patterns": record.matched_fraud_patterns,
                "business_address": record.business_address,
                "latitude": record.latitude,
                "longitude": record.longitude,
                "satellite_measured_area": record.satellite_measured_area,
                "area_discrepancy_percent": record.area_discrepancy_percent,
                "is_small_vendor": record.is_small_vendor,
                "lifestyle_analysis": record.lifestyle_analysis,
                "visual_analysis": record.visual_analysis,
                "network_analysis": record.network_analysis
            }
            session.close()
            return result
        session.close()
        return None
    except Exception as e:
        session.close()
        print(f"Error fetching record: {e}")
        return None


def get_risk_distribution() -> Dict[str, int]:
    session = get_db_session()
    if not session:
        return {}
    
    try:
        records = session.query(AnalysisRecord).all()
        distribution = {"LOW": 0, "MODERATE": 0, "HIGH": 0, "VERY HIGH": 0, "CRITICAL": 0}
        for r in records:
            if r.risk_level in distribution:
                distribution[r.risk_level] += 1
        session.close()
        return distribution
    except Exception as e:
        session.close()
        return {}


def get_business_type_fraud_stats() -> Dict[str, Dict]:
    session = get_db_session()
    if not session:
        return {}
    
    try:
        records = session.query(AnalysisRecord).all()
        stats = {}
        for r in records:
            bt = r.business_type
            if bt not in stats:
                stats[bt] = {"count": 0, "total_probability": 0, "high_risk_count": 0}
            stats[bt]["count"] += 1
            stats[bt]["total_probability"] += r.fraud_probability or 0
            if r.risk_level in ["HIGH", "VERY HIGH", "CRITICAL"]:
                stats[bt]["high_risk_count"] += 1
        
        for bt in stats:
            if stats[bt]["count"] > 0:
                stats[bt]["avg_probability"] = stats[bt]["total_probability"] / stats[bt]["count"]
        session.close()
        return stats
    except Exception as e:
        session.close()
        return {}


def get_state_wise_stats() -> Dict[str, Dict]:
    session = get_db_session()
    if not session:
        return {}
    
    try:
        records = session.query(AnalysisRecord).all()
        stats = {}
        for r in records:
            state = r.state or "Unknown"
            if state not in stats:
                stats[state] = {"count": 0, "total_probability": 0, "high_risk_count": 0, "total_revenue": 0}
            stats[state]["count"] += 1
            stats[state]["total_probability"] += r.fraud_probability or 0
            stats[state]["total_revenue"] += r.declared_revenue or 0
            if r.risk_level in ["HIGH", "VERY HIGH", "CRITICAL"]:
                stats[state]["high_risk_count"] += 1
        
        for state in stats:
            if stats[state]["count"] > 0:
                stats[state]["avg_probability"] = stats[state]["total_probability"] / stats[state]["count"]
        session.close()
        return stats
    except Exception as e:
        session.close()
        return {}


def delete_analysis_record(record_id: int) -> bool:
    session = get_db_session()
    if not session:
        return False
    
    try:
        record = session.query(AnalysisRecord).filter(AnalysisRecord.id == record_id).first()
        if record:
            session.delete(record)
            session.commit()
            session.close()
            return True
        session.close()
        return False
    except Exception as e:
        session.rollback()
        session.close()
        return False


def save_fraud_pattern(pattern_data: Dict) -> Optional[int]:
    session = get_db_session()
    if not session:
        return None
    
    try:
        pattern = FraudPattern(
            pattern_name=pattern_data.get("pattern_name"),
            pattern_type=pattern_data.get("pattern_type"),
            description=pattern_data.get("description"),
            key_indicators=pattern_data.get("key_indicators"),
            detection_rules=pattern_data.get("detection_rules"),
            risk_weight=pattern_data.get("risk_weight", 0.5),
            source=pattern_data.get("source"),
            source_url=pattern_data.get("source_url"),
            case_reference=pattern_data.get("case_reference")
        )
        session.add(pattern)
        session.commit()
        pattern_id = int(pattern.id)
        session.close()
        return pattern_id
    except Exception as e:
        session.rollback()
        session.close()
        print(f"Error saving fraud pattern: {e}")
        return None


def get_all_fraud_patterns() -> List[Dict]:
    session = get_db_session()
    if not session:
        return []
    
    try:
        patterns = session.query(FraudPattern).filter(FraudPattern.is_active == True).all()
        results = []
        for p in patterns:
            results.append({
                "id": p.id,
                "pattern_name": p.pattern_name,
                "pattern_type": p.pattern_type,
                "description": p.description,
                "key_indicators": p.key_indicators,
                "detection_rules": p.detection_rules,
                "risk_weight": p.risk_weight,
                "source": p.source,
                "case_reference": p.case_reference
            })
        session.close()
        return results
    except Exception as e:
        session.close()
        return []


def save_news_article(article_data: Dict) -> Optional[int]:
    session = get_db_session()
    if not session:
        return None
    
    try:
        existing = session.query(NewsArticle).filter(NewsArticle.url == article_data.get("url")).first()
        if existing:
            session.close()
            return existing.id
        
        article = NewsArticle(
            title=article_data.get("title"),
            url=article_data.get("url"),
            source=article_data.get("source"),
            published_date=article_data.get("published_date"),
            content=article_data.get("content"),
            summary=article_data.get("summary"),
            extracted_patterns=article_data.get("extracted_patterns"),
            fraud_types_mentioned=article_data.get("fraud_types_mentioned"),
            entities_mentioned=article_data.get("entities_mentioned"),
            amount_mentioned=article_data.get("amount_mentioned")
        )
        session.add(article)
        session.commit()
        article_id = int(article.id)
        session.close()
        return article_id
    except Exception as e:
        session.rollback()
        session.close()
        print(f"Error saving news article: {e}")
        return None


def get_recent_news_articles(limit: int = 50) -> List[Dict]:
    session = get_db_session()
    if not session:
        return []
    
    try:
        articles = session.query(NewsArticle).order_by(NewsArticle.scraped_at.desc()).limit(limit).all()
        results = []
        for a in articles:
            results.append({
                "id": a.id,
                "title": a.title,
                "url": a.url,
                "source": a.source,
                "published_date": a.published_date,
                "summary": a.summary,
                "fraud_types_mentioned": a.fraud_types_mentioned,
                "amount_mentioned": a.amount_mentioned,
                "is_processed": a.is_processed
            })
        session.close()
        return results
    except Exception as e:
        session.close()
        return []


def save_location_data(location_data: Dict) -> Optional[int]:
    session = get_db_session()
    if not session:
        return None
    
    try:
        location = LocationData(
            analysis_id=location_data.get("analysis_id"),
            business_name=location_data.get("business_name"),
            address=location_data.get("address"),
            latitude=location_data.get("latitude"),
            longitude=location_data.get("longitude"),
            place_id=location_data.get("place_id"),
            declared_area_sqft=location_data.get("declared_area_sqft"),
            measured_area_sqft=location_data.get("measured_area_sqft"),
            area_discrepancy=location_data.get("area_discrepancy"),
            polygon_coordinates=location_data.get("polygon_coordinates"),
            verification_status=location_data.get("verification_status", "pending")
        )
        session.add(location)
        session.commit()
        location_id = int(location.id)
        session.close()
        return location_id
    except Exception as e:
        session.rollback()
        session.close()
        print(f"Error saving location data: {e}")
        return None


def save_field_investigation(investigation_data: Dict) -> Optional[int]:
    session = get_db_session()
    if not session:
        return None
    
    try:
        investigation = FieldInvestigation(
            analysis_id=investigation_data.get("analysis_id"),
            vendor_analysis_id=investigation_data.get("vendor_analysis_id"),
            officer_name=investigation_data.get("officer_name"),
            officer_id=investigation_data.get("officer_id"),
            investigation_status=investigation_data.get("investigation_status", "pending"),
            priority=investigation_data.get("priority", "normal"),
            location=investigation_data.get("location"),
            gps_coordinates=investigation_data.get("gps_coordinates"),
            photos=investigation_data.get("photos"),
            notes=investigation_data.get("notes"),
            findings=investigation_data.get("findings"),
            follow_up_required=investigation_data.get("follow_up_required", False),
            follow_up_date=investigation_data.get("follow_up_date")
        )
        session.add(investigation)
        session.commit()
        investigation_id = int(investigation.id)
        session.close()
        return investigation_id
    except Exception as e:
        session.rollback()
        session.close()
        print(f"Error saving field investigation: {e}")
        return None


def get_pending_investigations(officer_id: str = None) -> List[Dict]:
    session = get_db_session()
    if not session:
        return []
    
    try:
        query = session.query(FieldInvestigation).filter(
            FieldInvestigation.investigation_status.in_(["pending", "in_progress"])
        )
        
        if officer_id:
            query = query.filter(FieldInvestigation.officer_id == officer_id)
        
        investigations = query.order_by(FieldInvestigation.created_at.desc()).all()
        results = []
        for inv in investigations:
            results.append({
                "id": inv.id,
                "created_at": inv.created_at,
                "analysis_id": inv.analysis_id,
                "vendor_analysis_id": inv.vendor_analysis_id,
                "officer_name": inv.officer_name,
                "status": inv.investigation_status,
                "priority": inv.priority,
                "location": inv.location,
                "follow_up_required": inv.follow_up_required
            })
        session.close()
        return results
    except Exception as e:
        session.close()
        return []


def get_vendor_analyses(limit: int = 100) -> List[Dict]:
    session = get_db_session()
    if not session:
        return []
    
    try:
        records = session.query(VendorAnalysis).order_by(VendorAnalysis.created_at.desc()).limit(limit).all()
        results = []
        for r in records:
            results.append({
                "id": r.id,
                "created_at": r.created_at,
                "vendor_name": r.vendor_name,
                "vendor_type": r.vendor_type,
                "location_description": r.location_description,
                "estimated_daily_revenue": r.estimated_daily_revenue,
                "declared_monthly_revenue": r.declared_monthly_revenue,
                "overall_fraud_score": r.overall_fraud_score,
                "risk_level": r.risk_level
            })
        session.close()
        return results
    except Exception as e:
        session.close()
        return []
