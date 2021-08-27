from flask import send_file, render_template, abort, current_app
from pathlib import Path

from .data.file_network_detail import FileNetworkDetail
from .data.file_network_summary import FileNetworkSummary


def nodes_latest_path(network_name: str) -> Path:
    return current_app.config.get('DATA_DIR') / network_name / "nodes_latest.pbz2"


def image_path(network_name: str) -> Path:
    return current_app.config.get('DATA_DIR') / network_name / "graph_latest.png"


def network_info_path(network_name: str) -> Path:
    return current_app.config.get('DATA_DIR') / network_name / "network_info.pbz2"


def network_detail(network_name):
    if network_name == 'favicon.ico':
        abort(404)
    fnd = FileNetworkDetail(network_name, current_app.config.get('DATA_DIR'))
    fnd.load()
    return render_template('network_detail.html',
                           headers=fnd.filtered_headers,
                           nodes=fnd.filtered_data,
                           network_name=network_name)


def get_network_image(network_name):
    return send_file(image_path(network_name), mimetype="image/png")


def network_summary(network_name):
    fns = FileNetworkSummary(network_name, current_app.config.get('DATA_DIR'))
    fns.load()

    return render_template('network_summary.html',
                           versions=fns.full_summary())
