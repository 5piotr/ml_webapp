from typing import Annotated, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from api.models import UserEstymations
from api.database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class UserEstymationsRequest(BaseModel):
    lat: float = Field(gt=48, lt=55)
    lng: float = Field(gt=14, lt=25)
    market: Literal['primary_market', 'aftermarket']
    build_year: int = Field(gt=1899, lt=2025)
    area: float = Field(gt=0, lt=999)
    rooms: int = Field(gt=0, lt=7)
    floor: int = Field(gt=-1, lt=16)
    floors: int = Field(gt=-1, lt=16)

@router.post('/estimate', status_code=status.HTTP_201_CREATED)
async def estimate_price(db: db_dependency, user_est_request: UserEstymationsRequest):
    est_model = UserEstymations(date=datetime.now(), ann_price=100, xgb_price=200,
                                **user_est_request.model_dump())
    
    db.add(est_model)
    db.commit()
