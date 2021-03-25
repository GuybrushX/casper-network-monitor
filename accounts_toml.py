import requests
import toml


def get_data(public_key: str) -> dict:
    resp = requests.get('https://raw.githubusercontent.com/CasperLabs/casper-node/release-1.0.0/resources/production/accounts.toml')
    a_toml = toml.loads(resp.text)

    accounts = a_toml.get("accounts", None)
    delegators = a_toml.get("delegators", None)

    output = {"key": public_key,
        "validator": None,
        "delegated_to": [],
        "delegation": []
    }

    for account in accounts:
        account_key = account.get("public_key", None)
        account_balance = account.get("balance", None)
        validator = account.get("validator", None)
        if validator is None:
            account_bonded_amount, account_delegation_rate = None, None
        else:
            account_bonded_amount = validator.get("bonded_amount", None)
            account_delegation_rate = validator.get("delegation_rate", None)

        if account_key == public_key:
            output["validator"] = {"key": account_key,
                                   "balance": account_balance,
                                   "bonded": account_bonded_amount,
                                   "delegation": account_delegation_rate}

    for delegator in delegators:
        validator_key = delegator.get("validator_public_key", None)
        delegator_key = delegator.get("delegator_public_key", None)
        balance = delegator.get("balance", None)
        delegated_amount = delegator.get("delegated_amount", None)
        if validator_key == public_key:
            output["delegated_to"].append({"val_key": validator_key,
                                           "del_key": delegator_key,
                                           "balance": balance,
                                           "delegated": delegated_amount})
        if delegator_key == public_key:
            output["delegation"].append({"val_key": validator_key,
                                        "del_key": delegator_key,
                                        "balance": balance,
                                        "delegated": delegated_amount})
    return output


if __name__ == '__main__':
    for key in ["010a78eef78966a56a633c665411388f97f850609960d5d898f3992272b8d4bcca",
                "019ecde420395f4a9b70be2d4db0ab914682e04705cc2d7d3d73d958c7e69bfff8",
                "01a60e0885f4968dd3107e088b4cb5798af665859b769bc1aa86909a5b67f66a66",
                "012034668d7a5844f4fce1c3672c8d54daa81adb6d230a4aeeccaa8b369f0178fc"]:
        print(get_data(key))
