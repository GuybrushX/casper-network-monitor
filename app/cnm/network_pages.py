from flask import send_file, render_template, abort, current_app
from pathlib import Path

from cnm.data.file_network_detail import FileNetworkDetail


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


# def network_summary(network_name):
#     # need to replace with template.
#     net_info = load_bz2_pickle(network_info_path(network_name))
#     nodes = load_bz2_pickle(nodes_latest_path(network_name))
#
#     valid_ver = defaultdict(int)
#     weight_pct = defaultdict(int)
#     all_ver = defaultdict(int)
#     node_count = 0
#     val_count = 0
#     for node in nodes.values():
#         node_count += 1
#         upgrade = "None"
#         if node["next_upgrade"]:
#             upgrade = node["next_upgrade"]["activation_point"]
#         version = f"{node['api_version']} - Upgrade: {upgrade}"
#         if node.get("is_validator"):
#             weight = node.get("weight_percent", 0)
#             weight_pct[version] += weight
#             valid_ver[version] += 1
#             val_count += 1
#         all_ver[version] += 1
#
#     versions = []
#     for key, val in all_ver.items():
#         versions.append({"version": key,
#                          "all_node_pct": round(val / node_count * 100, 2),
#                          "val_node_pct": round(valid_ver.get(key, 0) / val_count * 100, 2),
#                          "val_wgt_pct": round(weight_pct.get(key, 0), 2)})
#     return render_template('summary.html',
#                            peer_counts=net_info["peer_count"],
#                            path_counts=net_info["path_count"],
#                            versions=sorted(versions, key=lambda d: d["version"], reverse=True))
