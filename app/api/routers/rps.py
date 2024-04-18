import io
import numpy as np

from fastapi import APIRouter, Request, UploadFile, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

import tensorflow as tf
from PIL import Image, ImageFilter
from sklearn.cluster import KMeans
from plotly.offline import plot
import plotly.express as px

router = APIRouter(
    prefix='/rps_gesture_recognition',
    tags=['rps gesture recognition']
)

templates = Jinja2Templates(directory='api/templates')

IMG_SIZE = (92,70)

def cluster_resize_image(img):
    img_resized = img.resize(IMG_SIZE)
    img_array = np.array(img_resized)
    img_flat = img_array.reshape(-1,3)
    kmeans = KMeans(n_clusters=2, random_state=0, n_init='auto').fit(img_flat)

    for j in np.unique(kmeans.labels_):
        img_flat[kmeans.labels_==j,:] = kmeans.cluster_centers_[j]
    img_k = img_flat.reshape(img_array.shape)
    
    return img_resized, Image.fromarray(img_k)

def convert_image(img_k):
    img_e = img_k.convert('L')
    img_e = img_e.filter(ImageFilter.FIND_EDGES)
    return img_e.crop((1, 1, IMG_SIZE[0]-1, IMG_SIZE[1]-1))

def get_prediction(img_e):
    pred_dict = {0:'paper', 1:'rock', 2:'scissors'}
    model = tf.keras.models.load_model('api/rps_model/2024-04-09--18-41')
    img_e = np.array(img_e)
    img_e = img_e.reshape(1, IMG_SIZE[1]-2, IMG_SIZE[0]-2, 1)
    img_e = img_e/255
    pred = model.predict(img_e)
    label_no = np.argmax(pred)
    return pred_dict[label_no]

def generate_div_plots(*args):
    plots = []
    for image in args:
        fig = px.imshow(image)
        fig.update_layout(coloraxis_showscale=False, margin=dict(l=0,r=0,b=5,t=5), height=300,
                            paper_bgcolor='#051b11', hovermode=False, dragmode=False)
        fig.update_xaxes(showticklabels=False).update_yaxes(showticklabels=False)
        fig_div = plot(fig, output_type='div')
        plots.append(fig_div)
    return plots

@router.get('/', response_class=HTMLResponse, include_in_schema=False)
async def rps_estimator(request: Request):
    return templates.TemplateResponse('rps_gesture_recognition.html',
                                      {'request': request})

@router.post('/', response_class=HTMLResponse, include_in_schema=False)
async def rps_estimator(request: Request, picture: UploadFile = Form()):
    
    try:
        contents = await picture.read()
        img = Image.open(io.BytesIO(contents))
        
        img_r, img_k = cluster_resize_image(img)
        
        img_e = convert_image(img_k)

        label = get_prediction(img_e)

        plots = generate_div_plots(img_r, img_k, img_e)

    except:
        error_message = 'Something went wrong :('
        return templates.TemplateResponse('rps_gesture_recognition.html',
                                      {'request': request,
                                       'error_message': error_message})

    return templates.TemplateResponse('rps_gesture_recognition.html',
                                      {'request': request,
                                       'plot_div_r':plots[0],
                                       'plot_div_k':plots[1],
                                       'plot_div_e':plots[2],
                                       'label':label})

@router.get('/details', response_class=HTMLResponse, include_in_schema=False)
async def rps_estimator_details(request: Request):

    return templates.TemplateResponse('rps_cnn_details.html',
                                      {'request': request})
