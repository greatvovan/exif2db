from typing import Union, Optional
from datetime import datetime
from .types import Method, MethodNotFoundError


def dms2dd(degrees: int, minutes: int, seconds: int, direction: str) -> float:
    dd = degrees + (minutes / 60) + (seconds / 3600)
    if direction == 'S' or direction == 'W':
        dd = dd * -1
    return float(dd)    # For Pillow / Rational


def parse_exif_date(date: str, sub_sec: Union[str, int] = '000000') -> Optional[datetime]:
    if date is None:
        return None

    if len(date) > 19:
        date = date[:19]

    if sub_sec:
        return datetime.strptime(f'{date}.{sub_sec:0<6}', '%Y:%m:%d %H:%M:%S.%f')
    else:
        return datetime.strptime(date, '%Y:%m:%d %H:%M:%S')


def parse_method(method: str) -> Method:
    try:
        return Method[method.capitalize()]
    except KeyError:
        raise MethodNotFoundError(method)
