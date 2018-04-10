from datetime import datetime
from dateutil.parser import parse
import pytz
import math
import tzlocal

LOCAL_TIMEZONE = tzlocal.get_localzone()


def toUTC(suspectedDate):
    '''make a UTC date out of almost anything'''
    utc=pytz.UTC
    objDate=None
    if type(suspectedDate) == datetime:
        objDate = suspectedDate
    elif type(suspectedDate) == float:
        # This breaks in the year 2286
        EPOCH_MAGNITUDE = 9
        magnitude = int(math.log10(int(suspectedDate)))
        if magnitude > EPOCH_MAGNITUDE:
            suspectedDate = suspectedDate / 10 ** (magnitude - EPOCH_MAGNITUDE)
        objDate = datetime.fromtimestamp(suspectedDate, LOCAL_TIMEZONE)
    elif str(suspectedDate).isdigit():
        # epoch? but seconds/milliseconds/nanoseconds (lookin at you heka)
        epochDivisor = int(str(1) + '0'*(len(str(suspectedDate)) % 10))
        objDate = datetime.fromtimestamp(float(suspectedDate/epochDivisor), LOCAL_TIMEZONE)
    elif type(suspectedDate) in (str, unicode):
        if suspectedDate[0] == '-':
            # Negative number, so let's pick a date for them
            objDate = datetime(1970, 1, 1)
        else:
            objDate = parse(suspectedDate, fuzzy=True)
    try:
        if objDate.tzinfo is None:
            objDate=LOCAL_TIMEZONE.localize(objDate)
    except AttributeError as e:
        raise ValueError(
            "Date %s which was converted to %s has no "
            "tzinfo attribute : %s" % (suspectedDate, objDate, e))

    objDate=utc.normalize(objDate)

    return objDate
