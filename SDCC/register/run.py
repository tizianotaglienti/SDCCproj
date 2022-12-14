import argparse
import os
import pyfiglet
from src.main import Register

def run():
    # oggetto ArgumentParser mantiene le informazioni necessarie a parsare la linea di comando in tipi di dato di Python
    parser = argparse.ArgumentParser(description = 'Implementation of distributed election algorithms.\nRegister node.')

    # la chiamata al metodo seguente serve a riempire ArgumentParser con informazioni riguardo gli argomenti del programma
    parser.add_argument("-v", "--verbose", default = False, help = "increase output verbosity", action = "store_true")
    parser.add_argument("-c", "--config_file", action = "store", help = "needed a config file in json format")

    args = parser.parse_args()

    if not(args.config_file):
        parser.error("No json file passed")

    os.system("cls")    # comando Windows, non riconosciuto in ubuntu

    print(pyfiglet.figlet_format("REGISTER", font = "digital"))

    # chiamo oggetto Register con argomenti verbose e config_file ottenuti dal parser
    register = Register(args.verbose, args.config_file, False)
    # chiamata ai metodi receive e send definiti nel main
    register.receive()
    register.send()

if __name__ == '__main__':
    run()

