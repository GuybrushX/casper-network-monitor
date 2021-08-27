import time
from datetime import datetime, timedelta

from flask_apscheduler import APScheduler

from .scheduled_era_times import get_era_times
from .scheduled_network_info import generate_network_info

scheduler = APScheduler()


def start_scheduler(app):
    global scheduler
    # if you don't wanna use a config, you can set options here:
    # scheduler.api_enabled = True
    scheduler.init_app(app)
    scheduler.start()


def start_network_tasks(networks):
    global scheduler
    min_ahead = 1
    for network in networks:
        scheduler.add_job(id=f"era_times_{network.name}",
                          func=get_era_times,
                          trigger='date',
                          run_date=datetime.now() + timedelta(minutes=min_ahead),
                          args=[scheduler, network])
        scheduler.add_job(id=f"spider_{network.name}",
                          func=generate_network_info,
                          trigger="date",
                          run_date=datetime.now() + timedelta(minutes=min_ahead+1),
                          args=[scheduler, network])
        min_ahead += 2


