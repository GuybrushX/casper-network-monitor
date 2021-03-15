from flask import Flask, send_file, render_template
from pickle_util import load_bz2_pickle
from pathlib import Path

app = Flask(__name__)
SCRIPT_DIR = Path(__file__).parent.absolute()
DATA_FOLDER = SCRIPT_DIR / "data"


@app.route('/')
def nodes():
    nodes = load_bz2_pickle("data/nodes_latest.pbz2")
    return render_template('index.html', nodes=list(nodes.values()), network_name="delta-11")


@app.route('/img')
def get_image():
    return send_file("data/graph_latest.png", mimetype="image/png")


@app.route('/network')
def network_info():
    # need to replace with template.
    net_info = load_bz2_pickle("data/network_info.pbz2")
    output = ["<html><head><title>Delta-11 Network Details</title>",

              "</head><body>",
              f"<b>Node Count:</b> {net_info['node_count']}",
              "<p><table border=1><tr><th>Peer Count</th><th>One Way</th><th>Two Way</th></tr>"]
    for peer_count in net_info["peer_count"]:
        output.append("<tr>")
        for i in range(3):
            output.append(f"<td>{peer_count[i]}</td>")
        output.append("</tr>")
    output.append("</table><p>")
    output.append("<table border=1><tr><th>Path Len</th><th>Count</th></tr>")
    for path, count in net_info["path_count"]:
        output.append(f"<tr><td>{path}</td><td>{count}</td></tr>")
    output.append("</table>")
    output.append('<img src="./img" width="100%"/></html>')
    return ''.join(output)


@app.route('/ips')
def ips():
    return send_file("data/ips_latest.csv", mimetype='text/text')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
