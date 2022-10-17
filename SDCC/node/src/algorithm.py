from enum import Enum
import socket
import time
import signal as sign
import sys
import os
from . import helpers as help
from .constants import LISTENING, TOTAL_DELAY, BUFF_SIZE, HEARTBEAT_TIME, DEFAULT_ID
from abc import ABC, abstractmethod
from threading import Thread, Lock
from . import verbose as verb


class Type(Enum):

    """
    Class contains message types exchanged in Bully and Ring-based algorithm.
    """

    ELECTION = 0
    END = 1
    ANSWER = 2
    HEARTBEAT = 3
    REGISTER = 4
    ACK = 5