import pytz


def aware(utime):
    return pytz.timezone('Asia/Kolkata').localize(utime)
