import time
from typing import Annotated, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette import status
from starlette.responses import RedirectResponse
from api.models import AptEstymations
from api.database import SessionLocal

import pytz
import pickle
import tensorflow as tf
from xgboost import XGBRegressor

router = APIRouter(
    prefix='/apartment_price_estimator',
    tags=['apartment price estimator']
)

templates = Jinja2Templates(directory='api/templates')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class AptEstymationsRequest(BaseModel):
    lat: float = Field(gt=48, lt=55)
    lng: float = Field(gt=14, lt=25)
    market: Literal['primary', 'aftermarket']
    build_year: int = Field(gt=1899, lt=2025)
    area: int = Field(gt=0, lt=999)
    rooms: int = Field(gt=0, lt=7)
    floor: int = Field(gt=-1, lt=16)
    floors: int = Field(gt=-1, lt=16)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    'lat': 51.757193,
                    'lng': 19.451020,
                    'market': 'aftermarket',
                    'build_year': 2019,
                    'area': 55,
                    'rooms': 3,
                    'floor': 2,
                    'floors': 7
                }
            ]
        }
    }    

def get_current_timestamp():
    warsaw_tz = pytz.timezone('Europe/Warsaw') 
    timestamp = datetime.now(warsaw_tz).strftime('%Y-%m-%d_%H:%M:%S')
    return timestamp

def load_from_pkl(absolute_path):
    with open(absolute_path, 'rb') as file:
        return pickle.load(file)

def load_from_txt(absolute_path):
    with open(absolute_path, 'r') as file:
        return file.readline()
    
def get_cluster(lat, lng):
    kmeans = load_from_pkl('/models/kmeans.pkl')
    return kmeans.predict([[lat, lng]])[0]

def get_ann_pred(pred_frame):
    scaler = load_from_pkl('/models/scaler.pkl')
    ann_model = tf.keras.models.load_model('/models/ann.keras')
    ann_price = ann_model.predict(scaler.transform(pred_frame))[0][0]
    ann_price_m2 = ann_price/pred_frame.area.iloc[0]
    return round(ann_price), round(ann_price_m2)

def get_xgb_price(pred_frame):
    xgb_model = XGBRegressor()
    xgb_model.load_model('/models/xgb.json')
    xgb_price = xgb_model.predict(pred_frame)[0]
    xgb_price_m2 = xgb_price/pred_frame.area.iloc[0]
    return round(xgb_price), round(xgb_price_m2)

def get_apt_prices(lat, lng, market, build_year, area, rooms, floor, floors):
   
    cluster = get_cluster(lat, lng)
    pred_frame = load_from_pkl('/models/pred_frame.pkl')

    pred_frame['area'] = area
    pred_frame['build_yr'] = build_year
    if market == 'primary':
        pred_frame['market_primary_market'] = 1
    if rooms != 1:
        pred_frame['rooms_' + str(rooms)] = 1
    if floor != 0:
        pred_frame['floor_' + str(floor)] = 1
    if floors != 0:
        pred_frame['floors_' + str(floors)] = 1
    if cluster != 0:
        pred_frame['cluster_' + str(cluster)] = 1

    ann_price, ann_price_m2 = get_ann_pred(pred_frame)
    xgb_price, xgb_price_m2 = get_xgb_price(pred_frame)

    return ann_price, ann_price_m2, xgb_price, xgb_price_m2

@router.post('/api', status_code=status.HTTP_201_CREATED)
async def estimate_price(db: db_dependency, apt_est_request: AptEstymationsRequest,
                         request: Request):

    ann_price, ann_price_m2, xgb_price, xgb_price_m2 = \
        get_apt_prices(**apt_est_request.model_dump())

    est_model = AptEstymations(date=get_current_timestamp(),
                               ann_price=ann_price, ann_price_m2=ann_price_m2,
                               xgb_price=xgb_price, xgb_price_m2=xgb_price_m2,
                               source='api', ip_address=request.client.host,
                               **apt_est_request.model_dump())

    db.add(est_model)
    db.commit()

    return {'ann_price': ann_price, 'ann_price_m': ann_price_m2,
            'xgb_price': xgb_price, 'xgb_price_m': xgb_price_m2,
            'currency': 'PLN'}

@router.get('/api', status_code=status.HTTP_201_CREATED)
async def estimate_price(db: db_dependency,
                         request: Request,
                         lat: float = Query(gt=48, lt=55, default=51.757193),
                         lng: float = Query(gt=14, lt=25, default=19.451020),
                         market: Literal['primary', 'aftermarket'] = Query(),
                         build_year: int = Query(gt=1899, lt=2025, default=2019),
                         area: int = Query(gt=0, lt=999, default=55),
                         rooms: int = Query(gt=0, lt=7, default=3),
                         floor: int = Query(gt=-1, lt=16, default=2),
                         floors: int = Query(gt=-1, lt=16, default=7)):

    ann_price, ann_price_m2, xgb_price, xgb_price_m2 = \
        get_apt_prices(lat, lng, market, build_year, area,
                       rooms, floor, floors)

    est_model = AptEstymations(date=get_current_timestamp(),
                               ann_price=ann_price, ann_price_m2=ann_price_m2,
                               xgb_price=xgb_price, xgb_price_m2=xgb_price_m2,
                               source='api', ip_address=request.client.host,
                               lat=lat, lng=lng, market=market,
                               build_year=build_year, area=area,
                               rooms=rooms, floor=floor, floors=floors)

    db.add(est_model)
    db.commit()

    return {'ann_price': ann_price, 'ann_price_m': ann_price_m2,
            'xgb_price': xgb_price, 'xgb_price_m': xgb_price_m2,
            'currency': 'PLN'}

@router.get('/', response_class=HTMLResponse, include_in_schema=False)
async def price_estimator(request: Request):
    update_date = load_from_txt('/models/update.date')
    update_date = update_date.replace('_', ' ')
    return templates.TemplateResponse('apartment_price_estimator.html',
                                      {'request': request,
                                       'update_date': update_date})

@router.post('/', response_class=HTMLResponse, include_in_schema=False)
async def price_estimator(db: db_dependency, request: Request,
                          lat: float = Form(gt=48, lt=55, default=51.757193),
                          lng: float = Form(gt=14, lt=25, default=19.451020),
                          market: Literal['primary', 'aftermarket'] = Form(),
                          build: int = Form(gt=1899, lt=2025, default=2019),
                          area: int = Form(gt=0, lt=999, default=55),
                          rooms: int = Form(gt=0, lt=7, default=3),
                          floor: int = Form(gt=-1, lt=16, default=2),
                          floors: int = Form(gt=-1, lt=16, default=7)):

    ann_price, ann_price_m2, xgb_price, xgb_price_m2 = \
        get_apt_prices(lat, lng, market, build, area, rooms, floor, floors)

    est_model = AptEstymations(date=get_current_timestamp(),
                               lat=lat, lng=lng, market=market,
                               build_year=build, area=area, rooms=rooms,
                               floor=floor, floors=floors,
                               ann_price=ann_price, ann_price_m2=ann_price_m2,
                               xgb_price=xgb_price, xgb_price_m2=xgb_price_m2,
                               source='www', ip_address=request.client.host)

    db.add(est_model)
    db.commit()

    update_date = load_from_txt('/models/update.date')
    update_date = update_date.replace('_', ' ')

    time.sleep(5)
    return templates.TemplateResponse('apartment_price_estimator.html',
                                      {'request': request,
                                       'est_model': est_model,
                                       'update_date': update_date})
