#!/usr/bin/env python3

from networks import NETWORKS
from save_network_spider import save_data

for network in NETWORKS:
    save_data(network)
