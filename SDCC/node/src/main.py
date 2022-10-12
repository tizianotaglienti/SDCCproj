import json
import sys

from node.src import helpers as helpers, constants as constants, verbose as verbose


# crea classe Node che registra il nodo corrente alla rete e inizia un algoritmo tra i due definiti
class Node:

    # inizializza gli attributi dell'oggetto
    def __init__(self, verbose: bool, algorithm: bool, delay: bool):
        with open(config_path, "r") as config_file:
            config = json.load(config_file)

        self.ip = config["node"]["ip"]
        self.reg_port = config["register"]["port"]
        self.reg_ip = config["register"]["ip"]

        # self.algorithm = algorithm
        self.verbose = verbose
        self.delay = delay


    def start(self):


