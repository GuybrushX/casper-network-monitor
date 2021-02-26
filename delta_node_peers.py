import requests
from graphviz import Digraph
import json


def peer_to_ip(peer):
    return peer['address'].split(':')[0]


def ip_to_status(ip):
    return 'http://'+ip+':8888/status'


name = 'CL nodes'
our_urls = {'3.101.143.77', '52.53.167.243', '54.219.90.111', '13.52.248.209', '54.241.137.219', '54.153.119.5',
            '54.183.216.118', '13.52.249.146', '50.18.8.48', '54.215.90.102', '13.52.243.64', '3.101.43.165'}

visited = {}

dot = Digraph(comment='Peers visibility')


def visit(our_urls, url):
    contents = requests.get(url)
    json_content = contents.json()
    peers = json_content['peers']
    for peer in peers:
        ip = peer_to_ip(peer)
        if ip in our_urls:
            yield ip


for ip in our_urls:
    dot.node(ip)
    url = ip_to_status(ip)
    sees = list(visit(our_urls, url))
    for other in sees:
        dot.edge(ip, other, constraint='true')
    visited[ip] = sees

print(dot.source)
print(json.dumps(visited))
#dot.render('/tmp/peers.gv', view=True)
