from datetime import datetime
import pytz
TIMEZONE = pytz.timezone('America/Phoenix')

def now():
    return datetime.now(TIMEZONE)

def convert_secs(secs: float) -> dict:
    '''
    Convert a number of seconds into days, hours, minutes, seconds.
    '''
    
    if secs < 0: raise ValueError('Input must be greater than 0')
    
    SECS_TO_MIN = 60
    MINS_TO_HR = 60
    HOURS_TO_DAY = 24
    
    days, remainder_1 = divmod(secs,HOURS_TO_DAY*MINS_TO_HR*SECS_TO_MIN)
    hours, remainder_2 = divmod(remainder_1,MINS_TO_HR*SECS_TO_MIN)
    minutes, seconds = divmod(remainder_2,MINS_TO_HR*SECS_TO_MIN)
    
    return {
        'days': int(days),
        'hours': int(hours),
        'minutes': int(minutes),
        'seconds': int(seconds),
    }
    
def to_str(dnt_dict: dict[str, int]) -> str:
    days = dnt_dict['days']
    hours = dnt_dict['hours']
    minutes = dnt_dict['minutes']
    seconds = dnt_dict['seconds']
    
    results = []
    
    if days != 0:
        results.append(f'{days} day{'' if days == 1 else 's'}')
        
    if any(x!=0 for x in (days,hours)):
        results.append(f'{hours} day{'' if hours == 1 else 's'}')
        
    if any(x!=0 for x in (days,hours,minutes)):
        results.append(f'{minutes} day{'' if minutes == 1 else 's'}')
        
    if any(x!=0 for x in (days,hours,minutes,seconds)):
        results.append(f'{seconds} day{'' if seconds == 1 else 's'}')
    
    return ', '.join(results)