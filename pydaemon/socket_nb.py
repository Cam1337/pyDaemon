import socket, select, threading, Queue, time, sys

# socket.setdefaulttimeout(5)

class SocketEncapsulator(object):
    def __init__(self, sock):
        self.sock = sock
        self.sbuf = []
        self.rbuf = []
    def send(self, data):
        self.sbuf.append(data)
    def fileno(self):
        return self.sock.fileno()
    def recv(self, amt):
        self.sock.recv(amt)
    def close(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

class SocketConnector(threading.Thread):
    def __init__(self, _id, _in, out, timeout=0):
        threading.Thread.__init__(self)
        self.id      = _id
        self._in     = _in
        self.out     = out
        self.timeout = timeout # not implemented currently, no need since threads are working
        
        self.success = 0
        self.failed  = 0
        
        self.working = True
        
    def run(self):
        while self.working:
            try:
                host, port = self._in.get_nowait()
                connected_socket = self.connect(host, port)
                self.increment(connected_socket)
                if connected_socket: self.out.put(connected_socket)
            except Exception, e:
                print e
                self.working = False
                break
    def connect(self, host, port):
        try:
            new_sock = socket.socket()
            new_sock.connect((host, port))
            return SocketEncapsulator(new_sock)
        except Exception, e:
            return None
    def increment(self, sock):
        if sock:
            self.success += 1
        else:
            self.failed += 1
    @property
    def total(self):
        return self.success + self.failed
            

class ConnectionController(object):
    def __init__(self, hostpairs, numthreads, timeout):
        self.numthreads = numthreads
        self.timeout    = timeout
        
        self.threads = []
        self.sockets = []
        
        self.start = time.time()
        self.start_len = len(hostpairs)
        
        self.in_queue  = self.make_queue(hostpairs)
        self.out_queue = Queue.Queue()
    
    def make_queue(self, _list):
        nQueue = Queue.Queue()
        for item in _list:
            nQueue.put(item)    
        return nQueue    
    def connect_all(self):
        for _thread_id in xrange(self.numthreads):
            newThread = SocketConnector(_thread_id, self.in_queue, self.out_queue)
            newThread.daemon = True
            newThread.start()
            self.threads.append(newThread)
    def mainloop(self, on_read, on_write, on_error, on_garbage, garbage_args=False):
        while True:
            if len(self.sockets) == self.start_len:
                print time.time() - self.start
                self.close_all()
                break
            if len(self.sockets) != 0:
                read_list = self.sockets
                send_list = [sock for sock in self.sockets if sock.sbuf != []]
                err_list  = self.sockets
                
                _read, _write, _error = select.select(read_list, send_list, err_list, self.timeout)
                
                if _read:
                    for sock in _read:
                        on_read(sock)
                        
                if _write:
                    for sock in _write:
                        on_write(sock)
                
                if _error:
                    for sock in _error:
                        on_error(sock)
                
            if garbage_args:
                on_garbage(self.threads, self.sockets)
            else:
                on_garbage()
                
            self.garbage()
            
            if len(self.sockets) == 0:
                time.sleep(1)
    
    def garbage(self):
        self.threads = [_thread for _thread in self.threads if _thread.working]
        while True:
            try:
                self.sockets.append(self.out_queue.get_nowait())
            except:
                break
    def close_all(self):
        for _thread in self.threads:
            _thread.working = False
        for _socket in self.sockets:
            _socket.close()
            
        
class ExampleHandler(object):
    def __init__(self):
        pass
    def on_read(self, sock):
        print "Reading from sock: {0}".format(sock.fileno())
        sock.recv(1024) # remove recurring pending data
    def on_write(self, sock):
        print "Writing to sock: {0}".format(sock.fileno())
    def on_error(self, sock):
        print "Error from sock: {0}".format(sock.fileno())
    def on_garbage(self, threads, sockets):
        print "{0} threads running and {1} sockets connected".format(len(threads), len(sockets))
    
    
if __name__ == "__main__":
    hosts = [("python.org",80),("cam1337.info",80),("www.google.com",80)]
    controller = ConnectionController(hosts, 15, 5) # 15 threads, 5 seconds for select timeout
    
    example = ExampleHandler()
    
    controller.connect_all()
    try:
        controller.mainloop(example.on_read, example.on_write, example.on_error, example.on_garbage, True)
    except KeyboardInterrupt:
        controller.close_all()
        sys.exit("Closed all threads and sockets. Exiting cleanly.")
    