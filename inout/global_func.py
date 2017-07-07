import datetime, pytz

def aware(utime):
	return pytz.timezone('Asia/Kolkata').localize(utime)