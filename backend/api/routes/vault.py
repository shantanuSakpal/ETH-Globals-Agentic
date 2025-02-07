from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from models.vault import VaultCreate, VaultUpdate, VaultResponse, VaultList
from services.vault_service import VaultService
from api.middleware.auth import get_current_user
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=VaultResponse)
async def create_vault(
    vault: VaultCreate,
    current_user = Depends(get_current_user)
):
    """Create a new trading vault"""
    try:
        vault_service = VaultService()
        vault_data = await vault_service.create_vault(
            user_id=current_user["sub"],
            vault_params=vault.dict()
        )
        return vault_data
    except Exception as e:
        logger.error(f"Error creating vault: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating vault: {str(e)}"
        )

@router.get("/{vault_id}", response_model=VaultResponse)
async def get_vault(vault_id: str):
    """Get vault details"""
    try:
        vault_service = VaultService()
        vault = await vault_service.get_vault(vault_id)
        if not vault:
            raise HTTPException(
                status_code=404,
                detail=f"Vault {vault_id} not found"
            )
        return vault
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching vault {vault_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching vault: {str(e)}"
        )
