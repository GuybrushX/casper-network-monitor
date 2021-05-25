import datetime as dt
import pytz


era = 624
hours_ahead = 10*24
era_start = '2021-05-22T16:49:08.000Z'
time_format = '%Y-%m-%dT%H:%M:%S.000Z'

era_start_time = dt.datetime.strptime(era_start, time_format)
era_start_time = pytz.utc.localize(era_start_time)


def time_by_zone(date_time, zone):
    return pytz.timezone(zone).normalize(date_time)


next_start_time = era_start_time
for era_num in range(era+1, era + hours_ahead//2 + 1):
    next_start_time = next_start_time + dt.timedelta(hours=2)

    print(f"Era: {era_num}  {next_start_time} Z    "
          f"{time_by_zone(next_start_time, 'America/Los_Angeles')} P-US    "
          f"{time_by_zone(next_start_time, 'America/New_York')} E-US    "
          f"{time_by_zone(next_start_time, 'Europe/Berlin')} C-EUR")


# Era: 574  2021-05-18 12:32:42+00:00 Z    2021-05-18 05:32:42-07:00 P-US    2021-05-18 08:32:42-04:00 E-US    2021-05-18 14:32:42+02:00 C-EUR