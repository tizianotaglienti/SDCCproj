import json
import sys
from typing import Type

from . import helpers as helpers
from . import constants as constants
from . import verbose as verbose

from .algorithm import Type


# crea classe Node che registra il nodo corrente alla rete e inizia un algoritmo tra i due definiti

class Node:

    # inizializza gli attributi dell'oggetto
    def __init__(self, verbose: bool, algorithm: bool, config_path: str, delay: bool):
        with open(config_path, "r") as config_file:
            config = json.load(config_file)

        self.ip = config["node"]["ip"]
        self.reg_port = config["register"]["port"]
        self.reg_ip = config["register"]["ip"]

        # self.algorithm = algorithm
        self.verbose = verbose
        self.delay = delay

        self.coord = constants.DEFAULT_ID


    def start(self):
        # creazione socket tcp momentanea
        temporary_socket = helpers.create_socket(self.ip)

        # creazione socket sulla quale il nodo ascolta sempre
        listening_socket = helpers.create_socket(self.ip)
        listening_socket.listen()

        logging = verbose.set_logging()

        # usato il flag -v per offrire esecuzione "verbose"
        if self.verbose:
            # inserisce un messaggio di livello DEBUG sul logger
            logging.debug("Node: (ip:{} port:{})\nTriggered\n".format(listening_socket.getsockname()[0], listening_socket.getsockname()[1]))

        # richiesta al nodo register di unirsi alla rete
        msg = helpers.message(constants.DEFAULT_ID, Type['REGISTER'].value, listening_socket.getsockname()[1], listening_socket.getsockname()[0])
        destination = (self.reg_ip, self.reg_port)

        try:
            temporary_socket.connect(destination)
        except ConnectionRefusedError:
            print("Register node not available")
            listening_socket.close()
            sys.exit(1)

        temporary_socket.send(msg)

        # aspetta di ricevere la lista dei partecipanti alla rete
        data = temporary_socket.recv(constants.BUFF_SIZE)
        #if data["type"] == Type[el].value:
            #sono coord
        if not data:
            listening_socket.close()
            print("Register node crashed")
            sys.exit(1)

        msg = eval(data.decode('utf-8'))

        id = helpers.get_id(listening_socket.getsockname()[1], msg)

        verbose.logging_rx(self.verbose, logging, listening_socket.getsockname()[0], destination, id, msg)
        #print(msg[-1]["id"])
        #print(id)
        temporary_socket.close()

        # controlla se c'è un solo nodo
        if (len(msg) == 1):
            listening_socket.close()
            print("Not enough nodes generated")
            sys.exit(1)

        # si stabilisce subito un coordinatore
        if (id == msg[-1]["id"]):
            self.coordid = helpers.get_id(self.reg_port, msg)
            print("I am the coordinator!")


        #if self.algorithm:
         #   Bully(sock.getsockname()[0], sock.getsockname()[1], identifier,
          #        msg, sock, self.verbose, self.delay, self.algorithm, )
        #else:
         #   Ring(sock.getsockname()[0], sock.getsockname()[1], identifier,
          #       msg, sock, self.verbose, self.delay, self.algorithm,)
            #    a questo aggiungo come parametro anche l'id del coordinatore





