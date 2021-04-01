import datetime as dt
import pytz


era = 11
hours_ahead = 160
era_start = '2021-04-01T13:04:29.000Z'
time_format = '%Y-%m-%dT%H:%M:%S.000Z'

era_start_time = dt.datetime.strptime(era_start, time_format)
era_start_time = pytz.utc.localize(era_start_time)


def time_by_zone(date_time, zone):
    return pytz.timezone(zone).normalize(date_time)


next_start_time = era_start_time
for era_num in range(era+1, hours_ahead//2 + 1):
    next_start_time = next_start_time + dt.timedelta(hours=2)

    print(f"Era: {era_num}  {next_start_time} Z    {time_by_zone(next_start_time, 'America/New_York')} E    {time_by_zone(next_start_time, 'America/Los_Angeles')} W")
