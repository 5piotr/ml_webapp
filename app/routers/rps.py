from fastapi import APIRouter

router = APIRouter()

@router.get('/rps')
async def get_rps_pred():
    return {'rps_pred': 'rock'}
