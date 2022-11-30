import json
import socket
from random import randint
import time
from math import floor

def create_socket(ip: str) -> socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = (ip, 0)
    sock.bind(addr)
    return sock

def message(id: int, type: int, port: int, ip: str) -> bytes:
    # creazione messaggio per comunicare id, numero di porta e indirizzo ip
    msg = {'type': type, 'id': id, 'port': port, 'ip': ip}
    msg = json.dumps(msg)
    msg = str(msg).encode('utf-8')
    return msg

def get_id(port: int, list: list) -> int:
    # salva identificatore a partire dal numero di porta
    for item in list:
        if item.get('port') == port:
            return item.get('id')
    return 0

def get_index(id: int, list: list) -> int:
    index = 0
    for item in list:
        if item.get('id') == id:
            return index
        index += 1
    return 0

def delay(ub: int):
    # genera un tempo che il mittente aspetta prima di inviare il pacchetto
    # usato nei test
    delay = randint(0, floor(ub*1.5))
    time.sleep(delay)
