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
    # flag elected che si invia solo al nodo con id più alto per essere eletto insieme alla registrazione


    def __init__(self, ip: str, port: int, id: int, nodes: list, socket: socket, verbose: bool, delay: bool, algorithm: bool):

        self.ip = ip
        self.port = port
        self.id = id
        self.nodes = nodes
        self.socket = socket
        self.algorithm = algorithm

        self.coordid = DEFAULT_ID
        self.lock = Lock()

        # parametri passati da linea di comando
        self.delay = delay
        self.verbose = verbose

        sign.signal(sign.SIGINT, self.handler)

        self.logging = verb.set_logging()

        self.participant = False

        thread = Thread(target = self.listening)
        thread.daemon = True
        thread.start()

        self.start_election()
        Algorithm.heartbeat(self)
