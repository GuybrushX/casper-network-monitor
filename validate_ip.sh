#!/usr/bin/env bash


ip2dec(){ # Convert an IPv4 IP number to its decimal equivalent.
  declare -i a b c d
  IFS=. read a b c d <<<"$1"
  echo "$(((a<<24)+(b<<16)+(c<<8)+d))"
}

dec2ip(){ # Convert an IPv4 decimal IP value to an IPv4 IP.
  declare -i a=$((~(-1<<8))) b=$1
  set -- "$((b>>24&a))" "$((b>>16&a))" "$((b>>8&a))" "$((b&a))"
  local IFS=.
  echo "$*"
}

ip=$(cat /etc/casper/1_0_0/config.toml | grep public_address | grep -Po '(\d+\.){3}\d+')
if [ -z "$ip" ]
then
  echo "Unable to get IP from /etc/casper/1_0_0/config.toml.";
  exit 1
else
  echo "Using IP from /etc/casper/1_0_0/config.toml: $ip"
fi

ip_as_dec=$(ip2dec $ip)
if [ "$ip_as_dec" -eq "0" ]; then
  echo "Invalid conversion to decimal form"
  exit 2
else
  echo "Decmial form for transfer_id: $ip_as_dec"
fi

validation_account=016b74ac7946168a7c206a839a51c7ce03df3501f388b2d286a13bcf99d228dbbb
chain_name=delta-10
node_address=http://localhost:7777

echo "Transfering 1000 to validation address to verify IP."
casper-client transfer \
  --chain-name "$chain_name" \
  --node-address "$node_address" \
  --secret-key /etc/casper/validator_keys/secret_key.pem \
  --gas-price 1 \
  --amount 1000 \
  --payment-amount 10000 \
  --transfer-id "$ip_as_dec" \
  --target-account "$validation_account"
