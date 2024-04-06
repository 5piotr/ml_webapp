from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter(
    prefix='/rps_gesture_recognition',
    tags=['rps gesture recognition']
)

templates = Jinja2Templates(directory='api/templates')

@router.get('/details', response_class=HTMLResponse, include_in_schema=False)
async def price_estimator(request: Request):

    return templates.TemplateResponse('rps_cnn_details.html',
                                      {'request': request})
