from casper_node_util import NODE_ADDRESS, get_last_auction_era, get_auction_era_key_weight, get_proposer_per_block

BLOCKS_TO_CHECK = 500

key_weights = get_auction_era_key_weight(get_last_auction_era(NODE_ADDRESS))
total_weight = sum([weight for key, weight in key_weights])
block_count = 0

proposals = {key: 0 for key, weight in key_weights}
proposals["other"] = 0
for height, proposer in get_proposer_per_block()[-BLOCKS_TO_CHECK:]:
    if proposer in proposals:
        proposals[proposer] += 1
    else:
        proposals["other"] += 1
    block_count += 1


proposal_data = []
for key, weight in key_weights:
    key_proposals = block_count - proposals["other"]
    proposal_count = proposals[key]
    weight_pct = weight/total_weight*100
    prop_pct = proposal_count/key_proposals*100
    diff_pct = abs(weight_pct - prop_pct)/max(weight_pct, prop_pct) * 100
    proposal_data.append((key, weight, proposal_count, weight_pct, prop_pct, diff_pct))

print(f" Looking back {BLOCKS_TO_CHECK} blocks for proposer percentage")
print(f"                                                                   - wght  - prop  - diff")
print(f"         validator public key                                      - pct   - pct   - pct")
for data in sorted(proposal_data, key=lambda d: d[5]+d[3], reverse=True):
    print(f"{data[0]} - {data[3]:1.3f} - {data[4]:1.3f} - {data[5]:1.3f}")
print(f"Other proposals: {proposals['other']}")

