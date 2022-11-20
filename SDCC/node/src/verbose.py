import logging

def set_logging() -> logging:
    # configurazione logging specificando:
    # level: indica che tutti gli eventi al di sopra del livello DEBUG saranno registrati nel log
    # format: specifica il formato del messaggio di log
    # datefmt: usa lo stesso linguaggio di formattazione nel modulo datetime
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)s] %(asctime)s\n%(message)s",
        datefmt='%I:%M:%S'
    )
    return logging

def logging_rx(flag: bool, logging: logging, receiver: tuple, sender: tuple, id: int, data: list):
    if flag:
        logging.debug("Process: (ip: {}, port: {}, id: {})\nFrom: (ip: {}, port: {})\nMessage: {}\n".format(receiver[0], receiver[1], id, sender[0], sender[1], data))

def first_coordinator(flag: bool, logging: logging, id: int):
    if flag:
        logging.debug("Process {} is the coordinator".format(id))

def logging_tx(flag:bool, logging: logging, receiver: tuple, sender: tuple, id: int, data: list):
    if flag:
        logging.debug("Process: (ip: {}, port: {}, id: {})\nTo: (ip: {}, port: {})\nMessage: {}\n".format(sender[0], sender[1], id, receiver[0], receiver[1], data))
