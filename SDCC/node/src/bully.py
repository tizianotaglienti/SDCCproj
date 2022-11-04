from . import helpers as helpers
from .algorithm import Algorithm, Type
from .constants import DEFAULT_ID, TOTAL_DELAY, HEARTBEAT_TIME
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

    def __init__(self):
