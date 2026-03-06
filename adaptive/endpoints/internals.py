from fastapi import APIRouter

router = APIRouter()


# ==================== HEALTH CHECK ====================
@router.get("/health")
def health_check():
    """
    Vérifier que l'API fonctionne
    """
    return {"status": "healthy", "service": "AD Lab Deployment API"}
