# SDCCproj

## Specifica

Lo scopo del progetto è realizzare in \textbf{Python} un'applicazione distribuita che implementi gli algoritmi di elezione distribuita (Bully e Chang-Roberts).
Inoltre si implementano i servizi di Register e Heartbeat, oltre alle funzionalità di Verbose e Delay, utilizzabile tramite appositi flag da linea di comando.

## Esecuzione

Per l'esecuzione occorre utilizzare [Docker](https://www.docker.com/) e [Docker Compose](https://docs.docker.com/compose/). Inoltre c'è bisogno del file _requirements.txt_ per installare librerie esterne

```bash
# path SDCCproj/SDCC
pip install -r requirements.txt
```

### Esecuzione in locale senza container Docker - Tutti i flag

```bash
$ python run.py -h                                                     

usage: run.py [-h] [-v] [-d] [-a {ring,bully}] [-c CONFIG_FILE]

Implementation of distributed election algorithms. Generic node.

options:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity
  -d, --delay           generate a random delay to forwarding messages
  -a {ring,bully}, --algorithm {ring,bully}
                        ring by default
  -c CONFIG_FILE, --config_file CONFIG_FILE
                        needed a config file in json format
```

Le operazioni da seguire in ordine sono:

1 - Eseguire il nodo _register_:

```bash
# path SDCCproj/SDCC/register
python run.py -v -c ..\config.json
```

2 - Eseguire i nodi uno alla volta con:

```bash
# path SDCCproj/SDCC/node
python run.py -v -a bully -c ..\config.json
# senza scrivere "-a bully", in automatico verrà eseguito l'algoritmo Chang-Roberts
```

### Test

I test vanno eseguiti da linea di comando con i permessi di utente root, quindi bisogna eseguire cmd come amministratore:

```python
# path SDCCproj/SDCC
python test_ex.py
```

### Esecuzione remota su istanza EC2 con AWS usando container Docker

I comandi necessari per questa esecuzione sono:

```bash
# path Desktop

scp -i sdcckeys.pem -r SDCCproj/SDCC ubuntu@ip_instance:/home/ubuntu

ssh -i sdcckeys.pem ubuntu@ec2-ip.instance.compute-1.amazonaws.com
```

Una volta dentro, scaricare Docker e Docker Compose ed eseguire:

```
# path SDCCproj/SDCC
sudo docker-compose up
```
