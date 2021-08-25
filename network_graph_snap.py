import snap
from collections import defaultdict
from pathlib import Path
from time import process_time


SCRIPT_DIR = Path(__file__).parent.absolute()
DATA_FOLDER = SCRIPT_DIR / "data"


def all_ips_dict(nodes):
    ips = set()
    for node in nodes.values():
        ips.add(node["ip"])
        for ip in node["two_way_peers"]:
            ips.add(ip)
    return {ip: index for index, ip in enumerate(ips)}


def save_network_info(g, ip_index, nodes, network_info_file_path):
    peer_count = defaultdict(int)
    two_way_count = defaultdict(int)
    for node in nodes.values():
        # filter out peers from other network
        peers = len(set(node["peers"]).intersection(set(nodes.keys())))
        two_ways = len(node["two_way_peers"])
        peer_count[peers] += 1
        two_way_count[two_ways] += 1
    combined_count = []
    full_counts = set(peer_count.keys()).union(set(two_way_count.keys()))
    for count in sorted(full_counts, reverse=True):
        combined_count.append((count, peer_count.get(count, 0), two_way_count.get(count, 0)))

    path_len = defaultdict(int)
    for ip in ip_index.keys():
        for nip in ip_index.keys():
            try:
                id_a = ip_index[ip]
                id_b = ip_index[nip]
            except KeyError:
                continue
            if id_a == id_b:
                continue
            if id_a not in g:
                continue
            if id_b not in g:
                continue
            # This is really slow
            path_len[g.shortest_path_length(g, id_a, id_b)] += 1

    path_count = [(path, count) for path, count in sorted(path_len.items(), key=lambda d: d[0])]
    save_bz2_pickle({"node_count": len(nodes.keys()),
                     "peer_count": combined_count,
                     "path_count": path_count},
                    network_info_file_path)


def graph_nodes(nodes, image_file_path, network_info_file_path, fig_size=(20, 20)):
    g = snap.TUNGraph.New()
    ip_index = all_ips_dict(nodes)

    print("Build graph")
    start = process_time()
    for ip, index in ip_index.items():
        g.AddNode(index)

    for ip, index in ip_index.items():
        for peer_ip in nodes[ip]["two_way_peers"]:
            g.AddEdge(ip_index[ip], ip_index[peer_ip])
    print(f"Time: {process_time() - start}")

    for ip, index in ip_index.items():
        sp, _ = g.GetShortPathAll(index)
        print(ip, sp)

    # print("Plot")
    # start = process_time()
    # plt.figure(1, figsize=fig_size)
    # nx.draw(g, with_labels=True)
    # print(f"Time:{process_time() - start}")
    # plt.savefig(image_file_path)
    # plt.close()
    # print(f"Same Time finish save: {process_time() - start}")
    # print("Save Network Info")
    # start = process_time()
    # save_network_info(g, ip_index, nodes, network_info_file_path)
    # print(f"Time: {process_time() - start}")
    return list(ip_index.items())
