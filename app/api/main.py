from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from api.models import Base
from api.database import engine
from api.routers import rps, apt_estimator

import logging
logging.basicConfig(filename='app.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(
    title="MLApps",
    version="1.0",
    contact={
        "name": "My LinkedIn",
        "url": "https://www.linkedin.com/in/piotr-pi%C4%99tka-12a69693/"
    })

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory='api/templates')

app.mount('/static', StaticFiles(directory='api/static'), name='static')

app.include_router(rps.router)
app.include_router(apt_estimator.router)

@app.get('/healthy', include_in_schema=False)
def health_check():
    return {'status': 'healthy'}

@app.get('/', response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

@app.get('/privacy_policy', response_class=HTMLResponse, include_in_schema=False)
async def privacy_policy(request: Request):
    return templates.TemplateResponse('privacy_policy.html', {'request': request})

@app.get('/about', response_class=HTMLResponse, include_in_schema=False)
async def privacy_policy(request: Request):
    return templates.TemplateResponse('about.html', {'request': request})
