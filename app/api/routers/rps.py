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

@router.get('/', response_class=HTMLResponse, include_in_schema=False)
async def rps_estimator(request: Request):
    return templates.TemplateResponse('rps_gesture_recognition.html',
                                      {'request': request})

@router.post('/', response_class=HTMLResponse, include_in_schema=False)
async def rps_estimator(request: Request, picture: UploadFile = Form()):

    try:
        img_size = (92,70)
        pred_dict = {0:'paper', 1:'rock', 2:'scissors'}
        model = tf.keras.models.load_model('api/rps_model/2024-04-09--18-41')
        # load image
        contents = await picture.read()
        img = Image.open(io.BytesIO(contents))
        # resize
        img_resized = img.resize(img_size)
        # cast to array
        img_array = np.array(img_resized)
        # flatten for clustering
        img_flat = img_array.reshape(-1,3)
        # clustering
        kmeans = KMeans(n_clusters=2, random_state=0, n_init='auto').fit(img_flat)
        # generate clustered image
        for j in np.unique(kmeans.labels_):
            img_flat[kmeans.labels_==j,:] = kmeans.cluster_centers_[j]
        img_k = img_flat.reshape(img_array.shape)
        img_k = Image.fromarray(img_k)
        # convert to gray scale and fing edges
        img_e = img_k.convert('L')
        img_e = img_e.filter(ImageFilter.FIND_EDGES)
        # crop image to remove edges
        img_e = img_e.crop((1,1,img_size[0]-1,img_size[1]-1))
        # predict
        img_e_p = np.array(img_e)
        img_e_p = img_e_p.reshape(1, img_size[1]-2, img_size[0]-2, 1)
        img_e_p = img_e_p/255
        pred = model.predict(img_e_p)
        label_no = np.argmax(pred)
        label = pred_dict[label_no]

        # generating plots
        images = [img_resized,img_k,img_e]
        plots = []

        for image in images:
            fig = px.imshow(image)
            fig.update_layout(coloraxis_showscale=False, margin=dict(l=0,r=0,b=5,t=5), height=300,
                                paper_bgcolor='#051b11', hovermode=False, dragmode=False)
            fig.update_xaxes(showticklabels=False).update_yaxes(showticklabels=False)
            fig_div = plot(fig, output_type='div')
            plots.append(fig_div)

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
