from . import helpers as helpers
from . import constants as constants
from .algorithm import Algorithm, Type
import time
import socket
from . import verbose as verbose

class Bully(Algorithm):
    """
    In questo algoritmo si assume conoscenza e comunicazione completa tra processi.
    Si inizia con un coordinatore e, quando questo crasha,
        il primo processo che si accorge del fallimento fa partire un'elezione.
    Questo processo invia un messaggio ai soli processi con id superiore al suo.
    - se non riceve risposte si autoelegge coordinatore
    - se riceve risposte si disinteressa e l'algoritmo prosegue dai nodi che hanno risposto

    Complessivamente, i messaggi scambiati sono dei tipi: ELECTION, END, ANSWER, HEARBEAT, ACK.
    """
    # inizializza gli attributi dell'oggetto
    def __init__(self, ip: str, port: int, id: int, nodes: list, socket: socket, verbose: bool, delay: bool, algo: bool, coordid: int):
        #
        #
        Algorithm.__init__(self, ip, port, id, nodes, socket, verbose, delay, algo, coordid)


    # inizio di un'elezione
    def start_election(self):
        # si definisce un lock per gestire risorse condivise
        # dal momento che molti dati sono acceduti contemporaneamente da piu thread
        self.lock.acquire()

        # per far partire l'elezione contatto i nodi con id più grande del mio
        # prendo il mio index e lo incremento di 1
        # setto participant a true per essere nell'elezione
        # coord msg = False

    ----# se io sono il piu grande esco perche index == len
    |    # e quindi posso settarmi come coordinatore -> elezione finita: participant a False
    |   #
    |    # io leader avviso tutti i nodi (running process) inviando la forwarding di pacchetti END
    |        # (evito i processi morti perche fallisce la connect in quel caso)
    |    # se non c'è nessuno nella rete rimango in attesa infinita, per questo creo variabile close
    |        # close = True solo se mi risponde qualcuno (almeno 1) e quindi non termino l'esecuzione, altrimenti la termino
    |
    --> # se non sono il nodo piu grande invoco il metodo low_id_node (DEVO CHIAMARLO SOLO QUANDO CRASHO E NON ALL'INIZIO PERCHE IO INIZIO CON LEADER)
        # mi connetto e mando msg election ai nodi con id superiore al mio (for node in range (index, len))
        # la variabile exit funziona come close: se nessuno mi contatta sono io il leader e ritorno 1

    ---> # se ritorno 1 devo inviare i pacchetti di election (perche sono il capo) esco fuori dall'if con la freccetta disegnata

        # se ritorno 0 ho finito la start_election --> qualcuno mi ha risposto (piu grande di me) e vado in attesa


        # prima di ritornare 0, attendo le risposte (ANSWER) ai pacchetti che ho inviato per un certo tempo timeout

        # questi msg di answer non li aspetto quando li invio ma li aspetto nel metodo listening (algorithm.py)
        # quando ricevo un pacchetto, se il tipo e ANSWER allora rispondo con un pacchetto adeguato
            # ricevuto msg answer decremento la variabile globale checked_nodes ossia i nodi a cui ho inviato messaggio di elezione

        # dopo aver decrementato controllo
        # self.highernodes sara diverso da acknodes quindi il processo si aspetta un futuro messaggio di END perche qualcuno verra eletto
        # questa attesa si modella con furtherwaiting (endwait potrei chiamarlo)

        # VAI A FURTHERWAITING



    # fine di un'elezione
    def end(self, msg: dict):
        # lock management
        self.lock.acquire()
        # processo si autoelegge coordinatore
        self.coordid = msg["id"]
        # dopo essersi eletto coordinatore invia coord msg a tutti i running process
        self.coordmsg = True
        self.lock.release()



    # metodo che gestisce il processo di elezione
    def election(self, msg: dict):
        # lock management
        self.lock.acquire()

            # che succede?

        # quando ricevo pacchetto election rispondo con un answer
        # se non sto partecipando (False) e io ho id piu grande di chi contatto, io devo far partire l'elezione
        



    # metodo che gestisce la ricezione di un messaggio di risposta
    def answer(self):
        # lock management
        self.lock.acquire()
        self.highernodes -= 1
        self.lock.release()


    # metodo per l'inoltro di un messaggio
    def forwarding(self, nodes: dict, id: int, type: Type, connection: socket):
        # c'è un delay se viene specificato con flag da linea di comando
        helpers.delay(self.delay, constants.HEARTBEAT_TIME)

        destination = (node["ip"], node["port"])
        msg = helpers.message(id, type.value, self.port, self.ip)
        verbose.logging_tx(self.verb, self.logging, destination, (self.ip, self.port), self.id, eval(msg.decode('utf-8')))

        try:
            connection.send(msg)
        except ConnectionResetError:
            return



    #### e questi a che servono????

    #def low_id_node(self, index: int) -> int:

    #def further_waiting(self):

        # che succede in furtherwaiting?
        # per un certo tempo (while su un tempo) mi aspetto un msg di end
        # quando lo ricevo (lo vedo nella listening) vado a metodo end
        # setto il coordid e il coordmsg (TRUE) cioe ho ricevuto un msg di end
            # questo true significa che io ho avviato un'elezione che ha portato a un leader e che ora ho un leader

        # questo sta a indicare che l'elezione e finita, poi lo setto a False, lo azzero perche mi servira per la prox elezione

        # se non ho ricevuto nessun END ritorno 1 dal further wait, quindi ritorno 1 anche a low_id_node
        # quindi in questo caso l'if con la freccetta non si verifica e io sono il coord