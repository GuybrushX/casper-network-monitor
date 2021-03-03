from sseclient import SSEClient, Event
from pathlib import Path


class EventStreamReader:

    def __init__(self, server_address: str, last_id=0):
        self.server = server_address
        self.last_id = last_id

    def messages(self):
        """
        Blocking method that continuously yields messages from the SSE server.

        Updates self.last_id for each message.  If SSE queue outruns client and is disconnected,
        it will resume at last_id.
        """
        messages = SSEClient(self.server, last_id=self.last_id)
        for msg in messages:
            self.last_id = msg.id
            yield msg


class EventStreamSimulator:

    def __init__(self, dump_file: Path, last_id=0):
        self.file_path = dump_file
        self.last_id = last_id

    def messages(self):
        """
        Simulates live event stream by using a dump file of the event stream from:
        `curl -sN host_ip:9999/events > dump_file`
        """
        for_processing = []
        for line in open(self.file_path, 'r'):
            if line == "\n":
                if for_processing != [':\n']:
                    yield Event.parse(''.join(for_processing))
                for_processing = []
                continue
            for_processing.append(line)
