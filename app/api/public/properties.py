from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.properties.schema import PropertyResponse
from app.domains.properties.service import get_property_by_id, list_properties

router = APIRouter(prefix="/properties", tags=["Properties"])


@router.get("/", response_model=list[PropertyResponse])
def get_properties(db: Session = Depends(get_db)):
    return list_properties(db)


@router.get("/{property_id}", response_model=PropertyResponse)
def get_property(property_id: int, db: Session = Depends(get_db)):
    property_obj = get_property_by_id(db, property_id)
    if property_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        )
    return property_obj