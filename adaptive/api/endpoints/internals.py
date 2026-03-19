from fastapi import APIRouter, HTTPException

from adaptive.api.infrastructure import HypervisorProvider, ProxmoxProvider

router = APIRouter()


@router.get("/health")
def health_check():
    """
    Vérifier que l'API fonctionne
    """
    return {"status": "healthy", "service": "AD Lab Deployment API"}


@router.get("/health/hypervisor")
def hypervisor_health():
    """Test connectivity to the hypervisor."""
    hypervisor: HypervisorProvider = ProxmoxProvider()
    try:
        return hypervisor.check_connection()
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Hypervisor unreachable: {e}",
        ) from e
