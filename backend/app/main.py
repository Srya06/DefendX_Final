from fastapi import FastAPI, APIRouter
from app.api.v1 import auth, admin, profile

app = FastAPI(title="DEFEND-X API", version="1.0.0")

api_router = APIRouter(prefix="/api/v1")

@api_router.get("/health")
def health_check():
    return {"status": "ok", "service": "DEFEND-X API"}

# Include new real routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])

# Placeholders for Phase 3+
@api_router.get("/recruitment")
def recruitment_placeholder():
    return {"status": "Not Implemented - Phase 2"}
    
@api_router.get("/academics")
def academics_placeholder():
    return {"status": "Not Implemented - Phase 2"}

@api_router.get("/fitness")
def fitness_placeholder():
    return {"status": "Not Implemented - Phase 2"}

@api_router.get("/cv")
def cv_placeholder():
    return {"status": "Not Implemented - Phase 2"}

@api_router.get("/dri")
def dri_placeholder():
    return {"status": "Not Implemented - Phase 2"}

@api_router.get("/agents")
def agents_placeholder():
    return {"status": "Not Implemented - Phase 2"}

@api_router.get("/rag")
def rag_placeholder():
    return {"status": "Not Implemented - Phase 2"}

@api_router.get("/notifications")
def notifications_placeholder():
    return {"status": "Not Implemented - Phase 2"}

app.include_router(api_router)
