from app.db.database import SessionLocal, Base, engine
from app.models.recruitment import Force, SourceRegistry

def seed_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    forces = ["Indian Army", "Indian Navy", "Indian Air Force", "Police"]
    
    for f in forces:
        if not db.query(Force).filter(Force.name == f).first():
            db.add(Force(name=f))
            print(f"Added Force: {f}")
            
    sources = [
        {"force": "Indian Army", "org": "Join Indian Army", "url": "https://joinindianarmy.nic.in"},
        {"force": "Indian Navy", "org": "Join Indian Navy", "url": "https://joinindiannavy.gov.in"},
        {"force": "Indian Air Force", "org": "CDAC", "url": "https://afcat.cdac.in"},
        {"force": "Police", "org": "KSP", "url": "https://ksp.karnataka.gov.in"},
        {"force": "Central", "org": "UPSC", "url": "https://upsc.gov.in"}
    ]
    
    for s in sources:
        if not db.query(SourceRegistry).filter(SourceRegistry.official_url == s["url"]).first():
            db.add(SourceRegistry(
                force=s["force"],
                organization=s["org"],
                source_type="OFFICIAL_PORTAL",
                official_url=s["url"],
                name=s["org"]
            ))
            print(f"Added Source: {s['org']}")
            
    db.commit()
    db.close()

if __name__ == "__main__":
    print("Seeding database...")
    seed_db()
    print("Seeding complete.")
