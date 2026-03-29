import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.properties.schema import PropertyResponse
from app.domains.properties.service import get_property_by_id, list_properties

router = APIRouter(prefix="/properties", tags=["Properties"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=list[PropertyResponse])
def get_properties(db: Session = Depends(get_db)):
    properties = list_properties(db)
    logger.debug("Properties listed: count=%s", len(properties))
    return properties


@router.get("/{property_id}", response_model=PropertyResponse)
def get_property(property_id: int, db: Session = Depends(get_db)):
    property_obj = get_property_by_id(db, property_id)
    if property_obj is None:
        logger.warning("Property lookup failed: property_id=%s", property_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        )
    logger.debug("Property fetched: property_id=%s", property_id)
    return property_obj
