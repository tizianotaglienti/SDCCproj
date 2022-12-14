import logging
from random import randint
from . import constants as constants

def set_logging() -> logging:
    # configurazione logging specificando:
    # level: indica che tutti gli eventi al di sopra del livello DEBUG saranno registrati nel log
    # format: specifica il formato del messaggio di log
    # datefmt: usa lo stesso linguaggio di formattazione nel modulo datetime
    logging.basicConfig(
        level = logging.DEBUG,
        format = "[%(levelname)s] %(asctime)s\n%(message)s",
        datefmt = '%I:%M:%S'
    )
    return logging

def generate(list: list):
    # generazione ID tra 1 e 1000
    identifier = randint(constants.MIN, constants.MAX)
    if identifier not in list:
        return identifier
    else:
        generate(list)

def logging_rx(flag: bool, logging: logging, receiver: tuple, sender: tuple, id: int, data: list):
    if flag:
        logging.debug("Process: (ip:{} port:{} id:{})\nFrom: (ip:{} port:{})\nMessage: {}\n".format(receiver[0], receiver[1], id, sender[0], sender[1], data))

def logging_tx(flag: bool, logging: logging, receiver: tuple, sender: tuple, id: int, data: list):
    if flag:
        logging.debug("Process: (ip:{} port:{} id:{})\nTo: (ip:{} port:{})\nMessage: {}\n".format(sender[0], sender[1], id, receiver[0], receiver[1], data))
