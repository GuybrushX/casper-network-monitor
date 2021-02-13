import networkx as nx
import matplotlib.pyplot as plt


def all_ips_dict(nodes):
    ips = set()
    for node in nodes.values():
        ips.add(node["ip"])
        for ip in node["peers"]:
            ips.add(ip)
    return {ip: index for index, ip in enumerate(ips)}


def graph_nodes(nodes, filepath, fig_size=(20, 20)):
    g = nx.Graph()
    ip_index = all_ips_dict(nodes)

    for node in nodes.values():
        ip = node["ip"]
        for peer_ip in node["peers"]:
            g.add_edge(ip_index[ip], ip_index[peer_ip])
    plt.figure(1, figsize=fig_size)
    nx.draw(g, with_labels=True)
    plt.savefig(filepath)

    return list(ip_index.items())
