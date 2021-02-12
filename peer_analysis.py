from peer_spider import Spider, INTERNAL_NODES

spider = Spider(INTERNAL_NODES)
spider.get_all_nodes()

node_dict = spider.nodes
node_counts = []
for ip in node_dict.keys():
    peer_count = len(node_dict[ip]["peers"])
    have_my_ip = 0
    for node in node_dict.values():
        if ip in node["peers"]:
            have_my_ip += 1
    node_counts.append([ip, peer_count, have_my_ip, node_dict[ip]["peers"]])

print(node_counts)
