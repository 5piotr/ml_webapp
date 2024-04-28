from datetime import datetime
import pytz

def get_current_timestamp():
    warsaw_tz = pytz.timezone('Europe/Warsaw') 
    timestamp = datetime.now(warsaw_tz).strftime('%Y-%m-%d %H:%M:%S')
    return timestamp
