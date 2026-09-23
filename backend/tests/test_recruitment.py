import pytest
from app.models.recruitment import (
    Force, Exam, RecruitmentCategory, RecruitmentNotification, 
    PhysicalStandard, SourceRegistry, RawDocument, ExtractionStatus
)
from app.services.recruitment.pipeline import IngestionPipeline
from app.services.recruitment.parsers import ParserService

def test_force_and_exam_creation(db):
    f = Force(name="Indian Navy", description="Naval branch")
    db.add(f)
    db.commit()
    
    e = Exam(force_id=f.id, name="NDA", description="National Defence Academy")
    db.add(e)
    db.commit()
    
    assert f.id is not None
    assert e.id is not None
    assert e.force.name == "Indian Navy"

def test_get_forces_api(client, db):
    if not db.query(Force).filter(Force.name == "Indian Army").first():
        f = Force(name="Indian Army")
        db.add(f)
        db.commit()
        
    res = client.get("/api/v1/recruitment/forces")
    assert res.status_code == 200
    data = res.json()
    assert len(data) > 0
    assert any(d["name"] == "Indian Army" for d in data)

def test_get_notifications_with_target_force_filter(client, db):
    # Setup hierarchy
    f = Force(name="Police")
    db.add(f)
    db.commit()
    
    e = Exam(force_id=f.id, name="Sub Inspector")
    db.add(e)
    db.commit()
    
    c = RecruitmentCategory(exam_id=e.id, name="2026 Batch")
    db.add(c)
    db.commit()
    
    n = RecruitmentNotification(category_id=c.id, title="SI Recruitment 2026")
    db.add(n)
    db.commit()
    
    res = client.get("/api/v1/recruitment/notifications?target_force=Police")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["title"] == "SI Recruitment 2026"
    
    # Filter by non-existent force
    res2 = client.get("/api/v1/recruitment/notifications?target_force=SpaceForce")
    assert res2.status_code == 200
    assert len(res2.json()) == 0

def test_provenance_information(client, db):
    # Test that physical standards return provenance
    f = Force(name="IAF Test")
    db.add(f)
    db.commit()
    
    e = Exam(force_id=f.id, name="AFCAT")
    db.add(e)
    db.commit()
    
    c = RecruitmentCategory(exam_id=e.id, name="2026")
    db.add(c)
    db.commit()
    
    n = RecruitmentNotification(category_id=c.id, title="AFCAT 2026")
    db.add(n)
    db.commit()
    
    ps = PhysicalStandard(
        notification_id=n.id,
        text_content="Minimum height 157.5 cm",
        document_id="doc-123",
        page_start=14,
        source_url="https://afcat.cdac.in/official.pdf"
    )
    db.add(ps)
    db.commit()
    
    res = client.get(f"/api/v1/recruitment/physical-standards?notification_id={n.id}")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["text_content"] == "Minimum height 157.5 cm"
    assert data[0]["page_start"] == 14
    assert data[0]["source_url"] == "https://afcat.cdac.in/official.pdf"

def test_pipeline_validation_failure(db):
    source = SourceRegistry(
        force="Indian Army",
        organization="Join Indian Army",
        source_type="OFFICIAL_PORTAL",
        official_url="https://joinindianarmy.nic.in",
        name="JIA Portal"
    )
    db.add(source)
    db.commit()
    
    pipeline = IngestionPipeline(db)
    
    import asyncio
    # Trying to ingest from a completely different domain
    res = asyncio.run(pipeline.ingest_document(
        source_id=source.id, 
        url="https://fake-coaching-website.com/notification.pdf", 
        title="Fake Notif"
    ))
    
    assert res["status"] == "FAILED"
    assert res["reason"] == "VALIDATION_FAILED"
    assert "URL does not match official source domain" in res["detail"]
