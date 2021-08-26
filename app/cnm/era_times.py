from flask import render_template, redirect, current_app

from cnm.data.file_era_times import FileEraTimes
from cnm.casper_networks import network_by_name


def list_era_times(network_name, eras=90):
    MAX_ERAS = 200
    try:
        eras = int(eras)
    except ValueError:
        return redirect(f"/network/{network_name}/era_times")
    if eras > MAX_ERAS:
        return redirect(f"/network/{network_name}/era_times/{MAX_ERAS}")
    if eras < 0:
        return redirect(f"/network/{network_name}/era_times")
    config = network_by_name(network_name)
    fet = FileEraTimes(config, current_app.config.get("DATA_DIR"))
    fet.load()
    _, times = fet.walk_forward(1).__next__()
    time_zones = [zone for time, zone in times]
    era_data = []
    for era_id, times in fet.walk_forward(eras):
        cur_era = [era_id] + [time for time, zone in times]
        era_data.append(cur_era)
    return render_template("era_times.html", network_name=network_name, time_zones=time_zones, era_data=era_data)
