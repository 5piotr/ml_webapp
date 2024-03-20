from fastapi import APIRouter

router = APIRouter(
    prefix='/rps',
    tags=['rps gesture recognition']
)

@router.get('/estimate')
async def get_rps_pred():
    return {'rps_pred': 'rock'}
