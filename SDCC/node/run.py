import argparse
import os
import pyfiglet
from src.main import Node

def run():
    # oggetto ArgumentParser mantiene le informazioni necessarie a parsare la linea di comando in tipi di dato di Python
    parser = argparse.ArgumentParser(description='Implementation of distributed election algorithms.\nGeneric node.')

    # la chiamata al metodo seguente serve a riempire ArgumentParser con informazioni riguardo gli argomenti del programma
    parser.add_argument("-v", "--verbose", default=False, help="increase output verbosity", action="store_true")
    parser.add_argument("-d", "--delay", default=False, help="generate a random delay to forwarding messages", action="store_true")
    parser.add_argument("-a", "--algorithm", action='store', default="ring", choices=["ring", "bully"], help="ring by default")
    parser.add_argument("-c", "--config_file", action='store', help="needed a config file in json format")

    args = parser.parse_args()

    if not (args.config_file):
        parser.error('No json file passed')

    os.system("cls")    # comando Windows, non riconosciuto in ubuntu

    print(pyfiglet.figlet_format("NODE", font = "digital"))

    algorithm = False
    if args.algorithm == "bully":
        algorithm = True

    # chiamo oggetto Node con argomenti verbose e config_file ottenuti dal parser
    node = Node(args.verbose, algorithm, args.config_file, args.delay)
    # chiamata a metodo start definito nel main
    node.start()

if __name__ == '__main__':
    run()
