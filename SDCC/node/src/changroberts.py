from . import constants as constants
from . import helpers as helpers
from .algorithm import Algorithm, Type
from . import verbose as verbose
import sys
import os
import socket

# creazione classe ChangRoberts per l'esecuzione dell'algoritmo ring-based per l'elezione
class ChangRoberts(Algorithm):

    """
    La topologia è quella di un anello orientato dove i messaggi sono inviati in senso orario.
    Ogni processo conosce l'id degli altri (non anonymous) e manda il proprio id al nodo successivo nell'anello.
    Quando si riceve un messaggio:
    - se l'id ricevuto è maggiore del proprio -> si inoltra lo stesso messaggio
    - se l'id è uguale al proprio -> il ricevente elegge se stesso come coordinatore
    - se l'id è minore del proprio -> il messaggio viene ignorato e il ricevente manda il suo id al nodo successivo

    Complessivamente, i messaggi scambiati sono dei tipi: ELECTION, END, HEARTBEAT, ACK.
    """

    # inizializza gli attributi dell'oggetto
    def __init__(self, ip: str, port: int, id: int, nodes: list, socket: socket, verbose: bool, delay: bool, algorithm: bool, coordid: int):
        Algorithm.__init__(self, ip, port, id, nodes, socket, verbose, delay, algorithm, coordid)


    # inizio di un'elezione
    def start_election(self):
        # si definisce un lock per gestire risorse condivise
        # dal momento che molti dati sono acceduti contemporaneamente da piu thread
        self.lock.acquire()

        if (len(self.nodes) == 1):
            # se solo un nodo -> finish
            self.socket.close()
            sys.exit(1)

        self.participant = True
        if self.coordid == constants.DEFAULT_ID:
            # invia messaggio di tipo 0
            # per come si struttura il programma, questo avviene solo quando crasha un coordinatore
            self.forwarding(self.id, Type['ELECTION'])
        else:   # se coordid != -1  si tratta del futuro coordinatore
                # quel nodo invia subito un messaggio per concludere l'elezione (tipo 1)
            self.forwarding(self.id, Type['END'])
        self.lock.release()


    # fine di un'elezione
    def end(self, msg: dict):
        # lock management
        self.lock.acquire()

        # come detto nell'introduzione
        # quando l'id ricevuto è uguale al proprio, un processo si autoelegge coordinatore
        if self.coordid == self.id:
            self.lock.release()
            return

        self.participant = False
        self.coordid = msg["id"]
        # dopo essersi eletto coordinatore invia messaggi di tipo 1
        self.forwarding(msg["id"], Type['END'])
        self.lock.release()


    # metodo che gestisce il processo di elezione
    def election(self, msg: dict):
        # lock management
        self.lock.acquire()

        current_id = msg["id"]

        # quello che succede nel metodo end
        if current_id == self.id:
            self.participant = False
            self.coordid = self.id
            self.forwarding(current_id, Type['END'])
            self.lock.release()
            return

        elif current_id < self.id:
            # se id ricevuto < proprio id -> messaggio ignorato e se ne invia un altro di tipo 0 con il proprio id
            if self.participant == False:
                current_id = self.id
            else:
                self.lock.release()
                return

        # se id ricevuto > proprio id -> messaggio inoltrato al vicino
        self.participant = True
        self.forwarding(current_id, Type['ELECTION'])
        self.lock.release()

    # metodo che descrive inoltro di un messaggio
    def forwarding(self, id: int, type: Type):
        socket = helpers.create_socket(self.ip)
        # c'è un delay se viene specificato con flag da linea di comando
        helpers.delay(self.delay, constants.HEARTBEAT_TIME)

        index = helpers.get_index(self.id, self.nodes) + 1
        if index >= len(self.nodes):
            index = 0
        # scelta del processo successivo nell'anello
        node = self.nodes[index]
        msg = helpers.message(id, type.value, self.port, self.ip)

        try:
            destination = (node["ip"], node["port"])
            socket.connect(destination)     # connessione al processo successivo nell'anello
            verbose.logging_tx(self.verb, self.logging, destination, (self.ip, self.port), self.id, eval(msg.decode('utf-8')))
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

    def answer(self):
        # metodo che serve solo nel bully
        # in ChangRoberts non sono coinvolti messaggi di tipo 2
        pass