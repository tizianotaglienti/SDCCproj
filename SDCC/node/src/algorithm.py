from enum import Enum
import socket
import time
import signal as sign
from . import verbose as verbose

import sys
import os
from . import helpers as helpers
from .constants import LISTENING, TOTAL_DELAY, BUFF_SIZE, HEARTBEAT_TIME, DEFAULT_ID
from abc import ABC, abstractmethod
from threading import Thread, Lock


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
    #FIRSTCOORD = 6
    # flag elected che si invia solo al nodo con id più alto per essere eletto insieme alla registrazione

class Algorithm (ABC):

    # classe che verrà usata per i due algoritmi
    # definendo una Abstract Base Class si può definire un'API per un insieme di sottoclassi

    # inizializza gli attributi dell'oggetto
    def __init__(self, ip: str, port: int, id: int, nodes: list, socket: socket, verb: bool, delay: bool, algorithm: bool, coordid: int):

        self.ip = ip
        self.port = port
        self.id = id
        self.nodes = nodes
        self.socket = socket
        self.algorithm = algorithm

        self.coordid = coordid
        self.lock = Lock()

        # parametri passati da linea di comando
        self.delay = delay
        self.verb = verb

        sign.signal(sign.SIGINT, self.handler)

        self.logging = verbose.set_logging()

        self.participant = False

        # entrambi gli algoritmi inizializzano un listening thread
        thread = Thread(target = self.listening)
        thread.daemon = True
        thread.start()

        # un processo è gia eletto coordinatore alla fine della fase register
        # quindi l'algoritmo inizia con i processi che gli inviano messaggi di heartbeat attendendo ACK
        Algorithm.heartbeat(self)


    # metodi della classe di base
    # -------------
    @abstractmethod
    def start_election(self):
        pass

    @abstractmethod
    def answer(self):
        pass

    @abstractmethod
    def end(self, msg: dict):
        pass

    @abstractmethod
    def election(self, msg: dict):
        pass

    @abstractmethod
    def forwarding(self):
        pass
    # -------------


    # gestione di un processo interrotto (da linea di comando)
    def handler(self, signum: int, frame):
        self.logging.debug("Node: (ip: {}, port: {}, id: {})\nKilled\n".format(self.ip, self.port, self.id))
        self.socket.close()
        sys.exit(1)

    def listening(self):
        while True:
            self.lock.acquire()

            if self.coordid == self.id:
                self.socket.settimeout(LISTENING)
            else:
                self.socket.settimeout(None)
            self.lock.release()

            try:
                connection, address = self.socket.accept()
            except socket.timeout:
                self.logging.debug("Node: ip: {}, port: {}, id: {})\nFinish\n".format(self.ip, self.port, self.id))
                self.socket.close()
                os._exit(1)

            data = connection.recv(BUFF_SIZE)

            if not data:    # FIN ACK
                continue

            data = eval(data.decode('utf-8'))

            verbose.logging_rx(self.verb, self.logging, (self.ip, self.port),
                              address, self.id, data)

            # messaggio di tipo 3
            if data["type"] == Type['HEARTBEAT'].value:

                helpers.delay(self.delay, TOTAL_DELAY)

                msg = helpers.message(
                    self.id, Type['ACK'].value, self.port, self.ip)

                verbose.logging_tx(self.verb, self.logging, address,
                                  (self.ip, self.port), self.id, eval(msg.decode('utf-8')))

                connection.send(msg)
                connection.close()
                continue

            # messaggio di tipo 2
            elif data["type"] == Type['ANSWER'].value:
                self.answer()
                connection.close()
                continue

            func = {Type['ELECTION'].value: self.election,
                    Type['END'].value: self.end
                    }

            func[data["type"]](data)
            connection.close()


    def crash(self):
        # nel caso ChangRoberts si rimuove il nodo coordinatore
        if self.algorithm == False:
            self.nodes.pop()

        self.lock.release()
        self.start_election()

    # heartbeat serve a rilevare crash del coordinatore
    def heartbeat(self):
        while True:

            hb_sock = helpers.create_socket(self.ip)
            address = hb_sock.getsockname()

            time.sleep(HEARTBEAT_TIME)
            self.lock.acquire()

            # finché c'è un'elezione in corso non si mandano messaggi di heartbeat
            # inoltre il coordinatore non può mandare messaggi di heartbeat
            if self.participant or (self.coordid in [self.id, DEFAULT_ID]):
                self.lock.release()
                continue

            index = helpers.get_index(self.coordid, self.nodes)
            info = self.nodes[index]

            msg = helpers.message(
                self.id, Type['HEARTBEAT'].value, address[1], address[0])

            destination = (info["ip"], info["port"])


            try:
                hb_sock.connect(destination)
                hb_sock.send(msg)
                verbose.logging_tx(self.verb, self.logging, destination, (self.ip, self.port), self.id, eval(msg.decode('utf-8')))
                self.receive_ack(hb_sock, destination, TOTAL_DELAY)

            # il coordinatore crasha
            except ConnectionRefusedError:
                hb_sock.close()
                self.coordid = DEFAULT_ID   # conseguenza: nuova elezione
                self.crash()


    def receive_ack(self, sock: socket, destination: tuple, waiting: int):
        # si calcola il tempo iniziale con cui si calcola il tempo di attesa per il timeout
        start = round(time.time())
        sock.settimeout(waiting)

        try:
            data = sock.recv(BUFF_SIZE)
        except (socket.timeout, ConnectionResetError):
            sock.close()
            self.crash()
            return

        if not data:
            sock.close()
            self.crash()
            return

        msg = eval(data.decode('utf-8'))

        # viene ricevuto un pacchetto atteso
        if (msg["id"] == self.coordid) and (msg["type"] == Type["ACK"].value):
            self.lock.release()

        # ricevuto un pacchetto non valido
        else:
            stop = round(time.time())
            waiting -= (stop-start)     # ricalcolo del tempo di attesa
            self.receive_ack(sock, destination, waiting)       # ricorsione

        addr = (msg["ip"], msg["port"])
        verbose.logging_rx(self.verb, self.logging, destination, addr, self.id, msg)
        sock.close()

