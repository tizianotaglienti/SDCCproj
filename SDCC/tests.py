import signal
import psutil
from register.src.main import Register
from node.src.main import Node
from threading import Thread
import logging
import time
import sys
from multiprocessing import Process
from node.src import constants as nodeconstants
from random import randint
from register.src import constants as regconstants

TEST_DURATION = 5


class Tests:

    def __init__(self, nodes: int, algo: bool):
        self.nodenumber = nodes
        self.verbose = True
        self.nodes = []

        self.utils = Utils()
        self.logging = self.utils.set_logging()

        signal.signal(signal.SIGTERM, self.handler)

        thread_register = Thread(target=self.generate_register)
        thread_register.daemon = True
        thread_register.start()

        time.sleep(regconstants.SOCK_TIMEOUT/3)

        for _ in range(self.nodenumber):
            process = Process(target = self.utils.nodegen, args = (self.verbose, algo, True))
            process.daemon = True
            process.start()

        thread_register.join()

        self.logging.debug("Generated {} nodes\n\n{}\n".format(len(self.nodes), self.nodes))


    # test che descrive il fallimento di un nodo qualsiasi
    def test_any(self):

        time.sleep(nodeconstants.HEARTBEAT_TIME * TEST_DURATION)

        index = randint(0, self.nodenumber - 2)
        port = self.nodes[index]["port"]
        self.utils.nodekill(port)

        print("\nNODE {} KILLED\n\n".format(self.nodes[index]["id"]))

        time.sleep(nodeconstants.HEARTBEAT_TIME * TEST_DURATION)

        #self.utils.end(port, self.nodes)
        self.logging.debug("Test finished\n")

    # test che descrive il fallimento del nodo coordinatore
    def test_coord(self):

        time.sleep(nodeconstants.HEARTBEAT_TIME * TEST_DURATION)

        port = self.nodes[-1]["port"]
        self.utils.nodekill(port)

        print("\nNODE {} KILLED\n\n".format(self.nodes[-1]["id"]))

        time.sleep(nodeconstants.HEARTBEAT_TIME * TEST_DURATION)

        #self.utils.end(port, self.nodes)
        self.logging.debug("Test finished\n")

    # test che descrive il fallimento di un nodo qualsiasi e il coordinatore
    def test_both(self):

        time.sleep(nodeconstants.HEARTBEAT_TIME * TEST_DURATION)

        port = self.nodes[-1]["port"]
        self.utils.nodekill(port)
        print("\nNODE {} KILLED\n\n".format(self.nodes[-1]["id"]))


        index = randint(0, self.nodenumber - 2)
        port = self.nodes[index]["port"]
        self.utils.nodekill(port)
        print("\nNODE {} KILLED\n\n".format(self.nodes[index]["id"]))


        time.sleep(nodeconstants.HEARTBEAT_TIME * TEST_DURATION)

        #self.utils.end(port, self.nodes)
        self.logging.debug("Test finished\n")

    def generate_register(self):
        # metodo per simulare la fase di registrazione dei nodi ala rete
        register = Register(self.verbose, "./config.json", True)
        register.receive()
        register.send()
        self.nodes = register.get_list()

    def handler(self, signum: int, frame):
        print("Finish")
        sys.exit(1)


class Utils:

    def __init__(self):
        pass

    def nodegen(self, verbose: bool, algo: bool, delay: bool):
        node = Node(verbose, algo, "./config.json", delay)
        node.start()

    def nodekill(self, port: int):
        for node in psutil.process_iter():
            for connections in node.connections(kind='inet'):
                if connections.laddr.port == port:
                    try:
                        node.send_signal(signal.SIGTERM)
                    except psutil.NoSuchProcess:
                        pass

    def end(self, port: int, nodes: list):
        for index in range(len(nodes) - 1):
            numport = nodes[index]["port"]
            if numport == port:
                continue
            self.nodekill(numport)

    def set_logging(self) -> logging:
        # configurazione logging specificando:
        # level: indica che tutti gli eventi al di sopra del livello DEBUG saranno registrati nel log
        # format: specifica il formato del messaggio di log
        # datefmt: usa lo stesso linguaggio di formattazione nel modulo datetime
        logging.basicConfig(
            level=logging.DEBUG,
            format="[%(levelname)s] %(asctime)s\n%(message)s",
            datefmt='%b-%d-%y %I:%M:%S'
        )
        return logging

