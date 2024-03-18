from typing import Annotated, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from api.models import AptEstymations
from api.database import SessionLocal

import pytz
import pickle
import tensorflow as tf

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

def get_current_timestamp():
    warsaw_tz = pytz.timezone('Europe/Warsaw') 
    timestamp = datetime.now(warsaw_tz).strftime('%Y-%m-%d_%H:%M:%S')
    return timestamp

def load_from_pkl(absolute_path):
    with open(absolute_path, 'rb') as file:
        return pickle.load(file)
    
def get_cluster(lat, lng):
    kmeans = load_from_pkl('/models/kmeans.pkl')
    return kmeans.predict([[lat, lng]])[0]

def get_ann_pred(pred_frame):
    scaler = load_from_pkl('/models/scaler.pkl')
    ann_model = tf.keras.models.load_model('/models/ann.keras')
    ann_price = ann_model.predict(scaler.transform(pred_frame))[0][0]
    return int(ann_price)

def get_apt_prices(lat, lng, market, build_year, area, rooms, floor, floors):
   
    cluster = get_cluster(lat, lng)
    pred_frame = load_from_pkl('/models/pred_frame.pkl')

    pred_frame['area'] = area
    pred_frame['build_yr'] = build_year
    if market == 'primary_market':
        pred_frame['market_primary_market'] = 1
    if rooms != 1:
        pred_frame['rooms_' + str(rooms)] = 1
    if floor != 0:
        pred_frame['floor_' + str(floor)] = 1
    if floors != 0:
        pred_frame['floors_' + str(floors)] = 1
    if cluster != 0:
        pred_frame['cluster_' + str(cluster)] = 1

    ann_price = get_ann_pred(pred_frame)

    return ann_price, -1

@router.post('/estimate', status_code=status.HTTP_201_CREATED)
async def estimate_price(db: db_dependency, user_est_request: UserEstymationsRequest):

    ann_price, xgb_price = get_apt_prices(**user_est_request.model_dump())

    est_model = AptEstymations(date=get_current_timestamp(),
                               ann_price=ann_price, xgb_price=200.1,
                               **user_est_request.model_dump())

    db.add(est_model)
    db.commit()
