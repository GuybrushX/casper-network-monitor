from flask import Flask, send_file, render_template, abort, request, redirect
from flask_basicauth import BasicAuth
# from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename

from pathlib import Path
import shutil
from datetime import datetime
import gzip


import cnm.network_pages as network_pages
import cnm.era_times as era_times

import cnm.scheduled_tasks as scheduled_tasks
from cnm.protocol import get_chainspec_config_readme
from cnm.casper_networks import NETWORKS
import cnm.config as config

app = Flask(__name__)
SCRIPT_DIR = Path(__file__).parent.absolute()

ALLOWED_EXTENSIONS = {'gz'}
app.config['UPLOAD_FOLDER'] = config.UPLOAD_PATH
# Limit max upload to 100 MB
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

app.config['DATA_DIR'] = config.WEB_DATA
app.config['BASIC_AUTH_USERNAME'] = config.WEB_USER
app.config['BASIC_AUTH_PASSWORD'] = config.WEB_PASS
basic_auth = BasicAuth(app)

# app.config["MONGO_URI"] = config.MONGO_URI
# mongo = PyMongo(app)

scheduled_tasks.start_scheduler(app)
scheduled_tasks.start_network_tasks(NETWORKS)


@app.route('/')
def networks():
    return render_template('networks.html', networks=NETWORKS)


app.add_url_rule('/network/<network_name>/detail', view_func=network_pages.network_detail)
# app.add_url_rule('/network/<network_name>/summary', view_func=network_pages.network_summary)
app.add_url_rule('/network/<network_name>/img', view_func=network_pages.get_network_image)
app.add_url_rule('/network/<network_name>/era_times', view_func=era_times.list_era_times)
app.add_url_rule('/network/<network_name>/era_times/<eras>', view_func=era_times.list_era_times)


@app.route('/protocol/<network>/<protocol>')
def protocol_data(network, protocol):
    chainspec, config, readme = get_chainspec_config_readme(protocol, network)
    return render_template('protocol.html', chainspec=chainspec, config=config, readme=readme)


def _max_timestamp(key):
    key_path = config.UPLOAD_PATH / key
    return max([int(path.name) for path in key_path.glob('*')])


def valid_key(key: str) -> bool:
    if key[:2] == '01':
        return len(key) == 66
    if key[:2] == '02':
        return len(key) == 68
    return False


def _date_from_ts(timestamp):
    return str(datetime.utcfromtimestamp(timestamp))


@app.route('/debug_upload_script')
def debug_upload_script():
    return send_file(SCRIPT_DIR / "debug_upload_script.sh")


@app.route('/upload_debug_info', methods=['POST'])
# Upload with
# curl -F file=@<filename> key=<public_key> ts=<shared timestamp date +%s> http://127.0.0.1:8080/upload_debug_info
def upload_debug_info():
    file = request.files['file']
    key = request.form['key']
    ts = request.form['ts']
    if not key:
        return "key not received\n", 400
    else:
        if not valid_key(key):
            return "invalid key\n", 400
    if not file:
        return "file not received\n", 400
    if not ts:
        return "ts not received\n", 400

    save_folder = config.UPLOAD_PATH / secure_filename(key) / secure_filename(ts)
    save_folder.mkdir(parents=True, exist_ok=True)
    save_path = save_folder / secure_filename(file.filename)
    file.save(save_path)
    return "complete\n", 200


@app.route('/view_debug_info', defaults={'key': None, 'ts': None})
@app.route('/view_debug_info/<key>', defaults={'ts': None})
@app.route('/view_debug_info/<key>/<ts>')
@basic_auth.required
def view_debug_info(key, ts):
    if key is None and ts is None:
        key_times = sorted([(path.name, _max_timestamp(path.name)) for path in config.UPLOAD_PATH.glob('*')],
                           reverse=True,
                           key=lambda d: d[1])
        key_times = [(key, _date_from_ts(timestamp)) for key, timestamp in key_times]
        return render_template('debug_keys.html', key_times=key_times)
    if ts is None:
        key_path = config.UPLOAD_PATH / key
        ts_times = [(ts, _date_from_ts(int(ts))) for ts in sorted([path.name for path in key_path.glob('*')])]
        return render_template('debug_timestamps.html', key=key, ts_times=ts_times)
    full_path = config.UPLOAD_PATH / key / ts
    logs = sorted([path.name for path in full_path.glob('casper-node.log*gz')])
    err_logs = sorted([path.name for path in full_path.glob('casper-node.stderr.log*gz')])
    configs = sorted([path.name for path in full_path.glob('*_*_*.tar.gz')])
    reports = [path for path in full_path.glob('casper_node_report')]
    if reports:
        report = reports[0].read_text()
    return render_template('debug_full.html',
                           casper_node_report=report,
                           logs=logs,
                           err_logs=err_logs,
                           configs=configs,
                           key=key,
                           ts=ts)

@app.route('/archive_debug_info/<key>')
@basic_auth.required
def archive_debug_info(key):
    source_dir = config.UPLOAD_PATH / key
    target_dir = config.UPLOAD_PATH.parent / "debug_archive" / key
    shutil.move(source_dir, target_dir)
    return redirect("../../view_debug_info", 307)


@app.route('/download_debug_info/<key>/<ts>/<file>')
@basic_auth.required
def download_debug_info(key, ts, file):
    return send_file(config.UPLOAD_PATH / key / ts / file, mimetype="application/gzip")


@app.route('/tail_debug_logs/<key>/<ts>/<file>')
@basic_auth.required
def tail_debug_log(key, ts, file):
    from collections import deque
    path = config.UPLOAD_PATH / key / ts / file
    tail_count = 500
    lines = deque(maxlen=tail_count)
    with gzip.open(path, 'r') as f:
        for line in f:
            lines.append(line.decode('utf-8'))
    if len(lines) == 0:
        lines = ["empty"]
    return render_template("file_display.html", file_text="\n".join(lines))


@app.route('/grep_debug_logs/<key>/<ts>/<file>/<find>')
@basic_auth.required
def grep_debug_log(key, ts, file, find):
    from collections import deque
    path = config.UPLOAD_PATH / key / ts / file
    tail_count = 500
    lines = deque(maxlen=tail_count)
    with gzip.open(path, 'r') as f:
        for line in f:
            line_str = line.decode('utf-8')
            if find in line_str:
                lines.append(line_str)
    if len(lines) == 0:
        lines = ["empty"]
    return render_template("file_display.html", file_text="\n".join(lines))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8080")
