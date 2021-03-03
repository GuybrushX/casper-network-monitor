from event_stream_reader import EventStreamSimulator
from pathlib import Path
import json

dump_file = Path("saving_event_stream_delta-10")

sim = EventStreamSimulator(dump_file)

msg_type_set = set()
for msg in sim.messages():
    data = json.loads(msg.data)
    if isinstance(data, dict):
        msg_type = list(data.keys())[0]
        if msg_type not in msg_type_set:
            print(msg_type)
            msg_type_set.add(msg_type)
    # print(msg.id, msg.data)
