from dataclasses import dataclass
from enum import Enum

class PortState(str,Enum):
    OPEN = "open"
    CLOSED = "closed"
    FILTERED = "filtered"
    ERROR = "error"

@dataclass
class PortResult:
    # @dataclass automatically generates useful methods such as
    # __init__(), __repr__(), and equality comparison.
    #
    # This is useful because a scan can produce hundreds or thousands
    # of structured PortResult objects.

    host: str
    # IP address or hostname that was scanned.

    port: int
    # TCP/UDP port number, e.g. 22, 80, 443.
    protocol:str
    state:PortState
    latency_ms:float |None = None