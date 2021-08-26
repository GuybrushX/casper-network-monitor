#!/usr/bin/env bash

LOG_COUNT=3
RUN_TS=$(date +%s)
KEY=$(cat /etc/casper/validator_keys/public_key_hex)
SERVER_NAME="https://cnm.casperlabs.io"

upload () {
  echo "Uploading $1"
  curl -s -F file=@"$1" -F key="$KEY" -F ts="$RUN_TS" "$SERVER_NAME/upload_debug_info"
}

# Upload casper-node.log compressed archives
echo "Getting last $LOG_COUNT casper-node.log archive files."
for logfile in $(ls /var/log/casper/casper-node.log*gz | sort -r | head -n $LOG_COUNT)
do
  upload "$logfile"
done

echo

# Upload casper-node.stderr.log compressed archives
echo "Getting last $LOG_COUNT casper-node.stderr.log archive files."
for logfile in $(ls /var/log/casper/casper-node.stderr.log*gz | sort -r | head -n $LOG_COUNT)
do
  upload "$logfile"
done

echo

# Create and upload report
STATUS_FILENAME=${TMPDIR-/tmp}/casper_node_report
echo "Creating report file as $STATUS_FILENAME"

echo "$(uname -a)" > "$STATUS_FILENAME"
echo "$(lsb_release --description)" >> "$STATUS_FILENAME"
echo >> "$STATUS_FILENAME"
echo "Public Key: $KEY" >> "$STATUS_FILENAME"
echo >> "$STATUS_FILENAME"
echo "casper-node-launcher --version: $(casper-node-launcher --version)" >> "$STATUS_FILENAME"
echo >> "$STATUS_FILENAME"
printf "$(ls -la --recursive /etc/casper)" >> "$STATUS_FILENAME"
echo >> "$STATUS_FILENAME"
printf "$(ls -la --recursive /var/lib/casper)" >> "$STATUS_FILENAME"
echo >> "$STATUS_FILENAME"
printf "$(systemctl status casper-node-launcher)" >> "$STATUS_FILENAME"
echo >> "$STATUS_FILENAME"
printf "$(curl -s localhost:8888/status)" >> "$STATUS_FILENAME"

upload "$STATUS_FILENAME"

echo

# Get config files in /etc/casper/<protocol>
echo "Uploading config folder contents"
for config_dir in $(ls -d /etc/casper/*_*_*/)
do
  protocol=$(basename "$config_dir")
  config_archive=${TMPDIR-/tmp}/"$protocol".tar.gz
  echo "Archiving $config_dir into $config_archive"
  tar -czvf "$config_archive" -C "$config_dir" .
  upload "$config_archive"
done

echo
echo "To allow them to look at your debug files please give support staff:"
echo "$KEY / $RUN_TS"
