from fastapi import APIRouter

router = APIRouter(
    prefix='/rps',
    tags=['rps gesture recognition']
)

@router.get('/estimate', include_in_schema=False)
async def get_rps_pred():
    return {'app stataus': 'currently not working'}
