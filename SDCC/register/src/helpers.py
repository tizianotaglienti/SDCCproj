import json
import logging
import socket
from random import randint
from register.src import constants as constants

def set_logging() -> logging:
    logging.basicConfig(
        level = logging.DEBUG,
        format = "[%(levelname)s] %(asctime)s\n%(message)s",
        datefmt = '%b-%d-%y %I:%M:%S'
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
        logging.debug("Node: (ip:{} port:{} id:{})\nSender: (ip:{} port:{})\nMessage: {}\n".format(receiver[0], receiver[1], id, sender[0], sender[1], data))

def logging_tx(flag: bool, logging: logging, receiver: tuple, sender: tuple, id: int, data: list):
    if flag:
        logging.debug("[Node]: (ip:{} port:{} id:{})\n[Receiver]: (ip:{} port:{})\n[Message]: {}\n".format(sender[0], sender[1], id, receiver[0], receiver[1], data))
