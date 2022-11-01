from . import constants as constants
from . import helpers as helpers
from .algorithm import Algorithm, Type
from . import verbose as verbose
import sys
import os
import socket

class ChangRoberts(Algorithm):

    def __init__(self, ip: str, port: int, id: int, nodes: list, socket: socket, verbose: bool, delay: bool, algorithm: bool):
        Algorithm.__init__(self, ip, port, id, nodes, socket, verbose, delay, algorithm)

    def election_start(self):
        self.lock.acquire()

        if (len(self.nodes) == 1):
            self.socket.close()
            sys.exit(1)

        self.participant = True
        if self.coordid == constants.DEFAULT_ID:
            self.forwarding(self.id, Type['ELECTION'])
        else:   # coordid != -1 quindi si tratta del nodo già eletto coordinatore
                # allora quel nodo invia subito un messaggio per concludere l'elezione
            self.forwarding(self.id, Type['END'])
        self.lock.release()

    def end(self, msg: dict):
        self.lock.acquire()

        if self.coordid == self.id:
            self.lock.release()
            return

        self.participant = False
        self.coordid = msg["id"]
        self.forwarding(msg["id"], Type['END'])
        self.lock.release()

    def election_msg(self, msg: dict):
        self.lock.acquire()

        current_id = msg["id"]

        if current_id == self.id:
            self.participant = False
            self.coordid = self.id
            self.forwarding(current_id, Type['END'])
            self.lock.release()
            return

        elif current_id < self.id:
            if self.participant == False:
                current_id = self.id
            else:
                self.lock.release()
                return

        self.participant = True
        self.forwarding(current_id, Type['ELECTION'])
        self.lock.release()

    def forwarding(self, id: int, type: Type):
        socket = helpers.create_socket(self.ip)
        helpers.delay(self.delay, constants.HEARTBEAT_TIME)

        index = helpers.get_index(self.id, self.nodes) + 1
        if index >= len(self.nodes):
            index = 0

        node = self.nodes[index]
        msg = helpers.message(id, type.value, self.port, self.ip)

        try:
            destination = (node["ip"], node["port"])
            socket.connect(destination)
            verbose.logging_tx(self.verbose, self.logging, destination, (self.ip, self.port), self.id, eval(msg.decode('utf-8')))
            socket.send(msg)
            socket.close()

        except ConnectionRefusedError:
            self.nodes.pop(index)
            socket.close()
            if len(self.nodes) != 1:
                self.forwarding(id, type)
            else:
                self.socket.close()
                os.exit(1)
