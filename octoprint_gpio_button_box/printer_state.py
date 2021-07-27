from enum import Enum, auto

class PrinterState(Enum):
    Disconnected = auto()
    Operational = auto()
    Printing = auto()
    Paused = auto()
    Pausing = auto()
    Cancelling = auto()
    Error = auto()
