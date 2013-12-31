import socket

class RemoteSocket(object):
    def __init__(self, host, port, auth, proto):
        self.host = host
        self.port = port
        self.auth = auth
        self.conn = None
        self.receivebuffer = []
        self.sendbuffer    = []
        self.isconnected = False
        #protocol specifics
        self.terminator = proto["terminator"]
        self.timeout    = proto["timeout"]
        self.defrecvval = proto["recvamount"]
    def connect(self, arguments = ()):
        self.conn = socket.socket(*arguments)
        self.conn.connect((self.host, self.port))
        self.conn.setblocking(0)
        self.conn.send("connection spawned from nullbook at time {0}\n".format(__import__("time").time()))
        self.isconnected = True
    def fileno(self):
        if self.conn:
            return self.conn.fileno()
    def recv(self, amount):
        return self.conn.recv(amount)
    def recvall(self):
        partialbuffer = ""

    def writeall(self):
        pass
    def error(self):
        pass
    def garbage(self):
        pass
    def close(self):
        self.conn.shutdown(socket.SHUT_RDWR)
        self.conn.close()
        self.conn = None

class RemoteDatabase(object):
    def __init__(self, host, port, auth, dbms):
        self.host = host
        self.port = port
        self.auth = auth
        self.dbms = dbms
        self.conn = None
    def connect(self):
        pass