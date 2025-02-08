from fastapi import Depends
from cdp_langchain.utils import CdpAgentkitWrapper
from services.morpho import MorphoService

# Global service instances
_morpho_service: MorphoService = None

def get_cdp_wrapper() -> CdpAgentkitWrapper:
    """Get CDP toolkit wrapper instance"""
    return CdpAgentkitWrapper()

def get_morpho_service(
    cdp_wrapper: CdpAgentkitWrapper = Depends(get_cdp_wrapper)
) -> MorphoService:
    """Get Morpho service instance"""
    global _morpho_service
    if _morpho_service is None:
        _morpho_service = MorphoService(cdp_wrapper)
    return _morpho_service 