def get_weight_active_percent(self, validator_percent):
    """
    Returns active percent weight

    validator_percent is {key: percent_weight} dictionary
    """
    val_keys = set(validator_percent.keys())
    node_keys = set(self.active_node_keys())
    missing_keys = val_keys - node_keys
    missing = []
    full_set = []
    for key in val_keys:
        full_set.append((key, validator_percent[key], key not in missing_keys))
    for key, percent, active in sorted(full_set, key=lambda d: d[1], reverse=True):
        state = 'up' if active else ''
        print(f"{key}\t{round(percent, 2)}\t{state}")
    for key in missing_keys:
        missing.append((key, round(validator_percent[key], 2)))
    inactive_total = 0
    # print("\n\n\n")
    for key, percent in sorted(missing, key=lambda d: d[1], reverse=True):
        inactive_total += percent
        # print(f"{key} - Inactive validator with weight: {percent}%  -  ({round(inactive_total, 2)}% Total)")
    active_keys = val_keys.intersection(node_keys)
    return sum([weight for key, weight in validator_percent.items()
                if key in active_keys])

