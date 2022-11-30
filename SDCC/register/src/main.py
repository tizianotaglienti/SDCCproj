import socket
import json

from . import helpers as helpers
from . import constants as constants
import signal
import sys


# creazione classe Register che entra nella rete e offre la registrazione agli altri membri
class Register:
    # inizializza gli attributi dell'oggetto
    def __init__(self, verbose: bool, config_path: str, test: bool):
        with open(config_path, "r") as config_file:
            config = json.load(config_file)

        self.port = config["register"]["port"]
        self.ip = config["register"]["ip"]

        self.test = test
        if not test:
            signal.signal(signal.SIGINT, self.handler)

        # lista dei nodi inizialmente vuota
        self.nodes = []

        self.verbose = verbose
        self.logging = helpers.set_logging()

        # creazione socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # associazione socket con una specifica interfaccia di rete e un numero di porta
        self.sock.bind((self.ip, self.port))

        # inizializzazione lista di connessioni
        self.connections = []

    def receive(self):
        # il server si comporta da listening socket
        self.sock.listen()  # abilita il server ad accettare connessioni

        # usato il flag -v per offrire esecuzione "verbose"
        if self.verbose:
            # inserisce un messaggio di livello DEBUG sul logger
            self.logging.debug("Register = (ip: {}, port: {})\nTriggered\n".format(self.ip, self.port))

        # inizializzazione lista di identificatori
        ids = []

        # la socket rimane aperta per un tempo SOCK_TIMEOUT
        self.sock.settimeout(constants.REG_TIMEOUT)
        while True:
            try:
                conn, addr = self.sock.accept()     # la listening socket accetta connessioni

                # la funzione restituisce coppia (conn, addr):
                # conn è un nuovo oggetto socket utilizzabile per inviare e ricevere dati sulla connessione
                # addr è l'indirizzo legato al socket
                data = conn.recv(constants.BUFF_SIZE)   # riceve dati da socket
                msg = eval(data.decode('utf-8'))        # decodifica in utf-8

                if msg["type"] != constants.REGISTER:
                    conn.close()    # chiudo connessione
                    continue

                # generazione random di un id tra 1 e 1000
                id = helpers.generate(ids)

                # aggiunta di conn alla lista di connessioni
                self.connections.append(conn)

                # aggiunta di node alla lista di nodi registrati
                node = dict({'ip': addr[0], 'port': msg["port"], 'id': id})
                self.nodes.append(node)

                # stampa logger di ricezione
                helpers.logging_rx(self.verbose, self.logging, (self.ip, self.port), addr, 0, msg)

            except socket.timeout:
                break

        self.nodes.sort(key = lambda x: x["id"])


    def send(self):
        # codifica in utf-8
        data = str(self.nodes).encode('utf-8')

        for node in range(len(self.nodes)):
            ip = self.nodes[node]["ip"]
            port = self.nodes[node]["port"]
            id = self.nodes[node]["id"]
            helpers.logging_tx(self.verbose, self.logging, (ip, port), (self.ip, self.port), id, self.nodes)

            try:
                self.connections[node].send(data)
            except socket.timeout:
                print("No ack received from node with port {}\n". format(port))


    def handler(self, signum: int, frame):
        self.logging.debug("Register: (ip:{}, port:{})\nKilled\n".format(self.ip, self.port))
        self.close()

    def close(self):
        self.sock.close()
        sys.exit(1)

    def get_list(self) -> list:
        return self.nodes










