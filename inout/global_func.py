import datetime, pytz

def aware(utime):
	return pytz.utc.localize(utime)