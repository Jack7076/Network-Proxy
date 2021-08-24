import socket
import parse
import os
import sys
from pprint import pprint
from threading import Thread

class Proxy2Server(Thread):

    def __init__(self, host, port):
        super(Proxy2Server, self).__init__()
        self.client = None # Later Defined
        self.port   = port
        self.host   = host
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((host, port))
    def run(self):
        while True:
            data = self.server.recv(4096)
            if data:
                try:
                    reload(parse)
                    parse.parse(data, self.port, "server")
                except Exception as e:
                    print "server[{}] {}".format(self.port, e)
                # print "[{}] <- {}".format(self.port, data[:100].encode('hex'))
                # parse.parse(data, "p2s")
                self.client.sendall(data)

class Client2Proxy(Thread):
    
    def __init__(self, host, port):
        super(Client2Proxy, self).__init__()
        self.server = None # Server not known yet
        self.port   = port
        self.host   = host
        sock        = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(1)
        # Wait for client connection ...
        self.client, addr = sock.accept()
    
    def run(self):
        while True:
            data = self.client.recv(4096)
            if data:
                try:
                    reload(parse)
                    parse.parse(data, self.port, "client")
                except Exception as e:
                    print "client[{}] {}".format(self.port, e)
                # print "[{}] -> {}".format(self.port, data[:100].encode('hex'))
                # parse.parse(data, "c2p")
                self.server.sendall(data)

class Proxy(Thread):

    def __init__(self, from_host, from_port, to_host, to_port):
        super(Proxy, self).__init__()
        self.from_host = from_host
        self.to_host   = to_host
        self.from_port = from_port
        self.to_port   = to_port

    def run(self):
        while True:
            print "[Proxy] Setting Up ..."
            self.c2p = Client2Proxy(self.from_host,   self.from_port)
            self.p2s = Proxy2Server(self.to_host,     self.to_port)
            print "[Proxy] Connection Success!"
            self.c2p.server = self.p2s.server
            self.p2s.client = self.c2p.client
            print "[Proxy] Connections Bonded"
            self.c2p.start()
            self.p2s.start()

master_server = Proxy('127.0.0.1', 3000, '127.0.0.1', 25565)
master_server.start()

while True:
    try:
        cmd = raw_input('Proxy $ ')
        if(cmd[:4]) == 'quit':
            os._exit(0)
    except Exception as e:
        print e
