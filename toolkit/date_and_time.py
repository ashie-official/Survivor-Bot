from datetime import datetime
import pytz
TIMEZONE = pytz.timezone('America/Phoenix')

def now():
    return datetime.now(TIMEZONE)

def convert_secs(secs: float) -> str:
    '''
    Convert a number of seconds into days, hours, minutes, seconds.
    '''
    
    if secs < 0: raise ValueError('Input must be greater than 0')
    
    SECS_TO_MIN = 60
    MINS_TO_HR = 60
    HOURS_TO_DAY = 24
    
    days, remainder_1 = divmod(secs,SECS_TO_MIN*MINS_TO_HR*HOURS_TO_DAY)
    hours, remainder_2 = divmod(remainder_1,SECS_TO_MIN*MINS_TO_HR)
    minutes, seconds = divmod(remainder_2,SECS_TO_MIN)
    
    
    
    results = []
    
    if days != 0:
        results.append(f"{days} day{'' if days == 1 else 's'}")
        
    if any(x!=0 for x in (days,hours)):
        results.append(f"{hours} hour{'' if hours == 1 else 's'}")
        
    if any(x!=0 for x in (days,hours,minutes)):
        results.append(f"{minutes} minute{'' if minutes == 1 else 's'}")
        
    if any(x!=0 for x in (days,hours,minutes,seconds)):
        results.append(f"{seconds} second{'' if seconds == 1 else 's'}")
    
    return ', '.join(results)

def timezone_str(dt: datetime | str, format: str = "f") -> str:
    """
    Takes a datetime object or ISO-formatted string and returns a Discord timezone-adjusting string.
    
    Formats:
    
    (Default) f, Short Date/Time: `"May 26, 2026 5:00 PM"`
    
    F, Long Date/Time: `"Tuesday, May 26, 2026 5:00 PM"`
    
    d, Short Date: `05/26/2026`
    
    D, Long Date: `"May 26, 2026"`
    
    t, Short Time: `5:00 PM`
    
    T, Long Time: `5:00:00 PM`
    
    R, Relative Time: `in 5 minutes` / `2 hours ago`
    """
    
    if isinstance(dt, datetime): return f"<t:{int(dt.timestamp())}:{format}>"
    if isinstance(dt, str): return f"<t:{int(datetime.fromisoformat(dt).timestamp())}:{format}>" 