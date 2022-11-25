from . import helpers as helpers
from . import constants as constants
from .algorithm import Algorithm, Type
import time
import socket
import os
from . import verbose as verbose

# creazione classe Bully per l'esecuzione dell'algoritmo Bully
class Bully(Algorithm):

    # in questo algoritmo si assume conoscenza e comunicazione completa tra processi
    #
    # si inizia con un coordinatore e, quando questo crasha,
    #     il primo processo che si accorge del fallimento fa partire un'elezione
    #
    # questo processo invia un messaggio ai soli processi con id superiore al suo:
    # - se non riceve risposte si autoelegge coordinatore
    # - se riceve risposte si disinteressa e l'algoritmo prosegue dai nodi che hanno risposto
    #
    # complessivamente, i messaggi scambiati sono dei tipi: ELECTION, END, ANSWER, HEARBEAT, ACK


    # inizializza gli attributi dell'oggetto
    def __init__(self, ip: str, port: int, id: int, nodes: list, socket: socket, verbose: bool, delay: bool, algo: bool, coordid: int):
        self.highernodes = 0
        self.coordmsg = False
        Algorithm.__init__(self, ip, port, id, nodes, socket, verbose, delay, algo, coordid)


    # inizio di un'elezione
    def start_election(self):
        # si definisce un lock per gestire risorse condivise
        # dal momento che molti dati sono acceduti contemporaneamente da piu thread
        self.lock.acquire()

        # per far partire l'elezione un processo contatta i nodi con id maggiore del suo
        index = helpers.get_index(self.id, self.nodes) + 1      # prende il suo index e lo aumenta di 1
        self.participant = True     # per essere coinvolto nell'elezione
        self.coordmsg = False

        if (index != len(self.nodes)) and (self.lowest(index) == 0):
            return
        # se il processo è il più grande, index == len
        # allora si imposta come coordinatore e l'elezione finisce
        self.coordid = self.id
        self.participant = False

        # successivamente il processo avvisa tutti gli altri (running) inviando pacchetti END
        # si evitano i processi morti per fallimento della connect
        close = False
        for node in range (len(self.nodes) - 1):
            socket = helpers.create_socket(self.ip)
            if node == (index - 1):
                continue
            try:
                socket.connect((self.nodes[node]["ip"], self.nodes[node]["port"]))
                close = True
                self.forwarding(self.nodes[node], self.id, Type["END"], socket)
                socket.close()
            except ConnectionRefusedError:
                socket.close()
                continue

        # se non c'è nessuno nella rete si rimane in attesa infinita, per questo si crea la variabile close
        # close = True solo se risponde qualcuno, altrimenti si termina l'esecuzione
        if not close:
            self.logging.debug("Node: (ip: {}, port: {}, id: {})\nFinish\n".format(self.ip, self.port, self.id))
            self.socket.close()
            os._exit(1)

        self.lock.release()

    # se index != len(self.nodes) si passa al controllo successivo
    def lowest(self, index: int) -> int:
        # viene chiamato quando il leader crasha
        # non all'inizio perché si parte con un leader subito dopo la registrazione
        self.coordid = constants.DEFAULT_ID

        self.highernodes = len(self.nodes) - index
        ackednodes = self.highernodes


        exit = False

        # il processo si connette e manda messaggio di tipo ELECTION a chi ha id superiore al suo
        for node in range (index, len(self.nodes)):
            socket = helpers.create_socket(self.ip)
            try:
                socket.connect((self.nodes[node]["ip"], self.nodes[node]["port"]))
                self.forwarding(self.nodes[node], self.id, Type["ELECTION"], socket)
                socket.close()
                exit = True
            except ConnectionRefusedError:
                socket.close()
                continue


        if exit == False:
            return 1
        self.lock.release()

        timeout = time.time() + constants.TOTAL_DELAY
        while (time.time() < timeout):
            self.lock.acquire()

            # se highernodes != ackednodes, il processo si aspetta un futuro messaggio di END, perché qualcuno verrà eletto
            # questa attesa si modella con il metodo endwait
            if self.highernodes != ackednodes:
                self.lock.release()

                if self.endwait() == 0:
                    return 0
                else:
                    return 1

            self.lock.release()

        self.lock.acquire()
        return 1

        # se ritorna 1 bisogna inviare i pacchetti di election
        # in questo caso si esce fuori dall'if iniziale

        # se ritorna 0 finisce la start_election -> qualcuno con id maggiore ha risposto e si va in attesa
        # ma prima di ritornare 0 si attendono per un certo timeout le ANSWER ai pacchetti che ho inviato
            # questi messaggi si attendono nel metodo listening (algorithm.py)


    # fine di un'elezione
    def end(self, msg: dict):
        # lock management
        self.lock.acquire()
        # processo si autoelegge coordinatore
        self.coordid = msg["id"]
        # dopo essersi eletto coordinatore invia coord msg a tutti i running process
        self.coordmsg = True        # questo significa che viene ricevuto un messaggio di END
            # coordmsg = True significa che il processo ha avviato un'elezione che ha portato a trovare un leader
        self.lock.release()


    # metodo che gestisce la ricezione di un messaggio di risposta
    # ricevuto answer msg si decrementa la variabile globale highernodes
    def answer(self):
        # lock management
        self.lock.acquire()
        self.highernodes -= 1
        self.lock.release()

    def endwait(self):
        timeout = time.time() + constants.TOTAL_DELAY
        # per un certo tempo si aspetta un messaggio END
        while(time.time() < timeout):
            self.lock.acquire()
            # quando viene ricevuto (listening) si va in metodo end
            if self.coordmsg == True:       # elezione finita, ricevuto messaggio END
                self.participant = False
                self.coordmsg = False
                # imposto parametri a False per riutilizzarli alla prossima elezione
                self.lock.release()
                return 0
            self.lock.release()
        # se non si riceve nessun END si ritorna 1, quindi ritorna 1 anche il metodo lowest
        # in questo caso l'if iniziale non si verifica e il processo si elegge coordinatore
        self.lock.acquire()
        self.participant = False
        return 1


    # metodo che gestisce il processo di elezione
    def election(self, msg: dict):
        # lock management
        self.lock.acquire()
        socket = helpers.create_socket(self.ip)

        try:
            socket.connect((msg["ip"], msg["port"]))
            # quando si riceve un pacchetto ELECTION, si risponde con uno ANSWER
            self.forwarding(msg, self.id, Type['ANSWER'], socket)
        except ConnectionRefusedError:
            pass

        socket.close()

        if self.participant == False:
            # se il processo non sta partecipando all'elezione
            self.lock.release()
            # significa che questo ha id più grande di chi contatta
            # e quindi deve far partire l'elezione
            self.start_election()
            return

        self.lock.release()


    # metodo per l'inoltro di un messaggio
    def forwarding(self, nodes: dict, id: int, type: Type, connection: socket):
        # c'è un delay se viene specificato con flag da linea di comando
        helpers.delay(self.delay, constants.HEARTBEAT_TIME)

        destination = (nodes["ip"], nodes["port"])
        msg = helpers.message(id, type.value, self.port, self.ip)
        verbose.logging_tx(self.verb, self.logging, destination, (self.ip, self.port), self.id, eval(msg.decode('utf-8')))

        try:
            connection.send(msg)
        except ConnectionResetError:
            return