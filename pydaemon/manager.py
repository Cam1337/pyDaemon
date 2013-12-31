import select

class MonitorManager(object):
    def __init__(self):
        self.monitors = []

class NetworkManager(object):
    def __init__(self, networks, timeout=None):
        self.networks = networks
        for network in networks:
            if not network.isconnected:
                network.connect()
        if timeout == None:
            self.timeout = sum([n.timeout for n in self.networks]) / (1.0 * len(self.networks)) # average
        else:
            self.timeout = timeout
    def check(self):
        if self.networks == []:
            return

        readcount = errorcount = writecount = 0
        readlist  = errorlist  = self.networks
        writelist = [network for network in self.networks if network.sendbuffer != []]

        read, write, error = select.select(readlist, writelist, errorlist, self.timeout)

        if read:
            for network in read:
                readcount += 1
                network.recvall()
        if write:
            writecount += 1
            for network in write:
                network.writeall()
        if error:
            errorcount += 1
            for network in error:
                network.error()
                self.networks.remove(network)

        for network in self.networks:
            network.garbage()

        return (readcount, writecount, errorcount) # same order as select.select parameters


class Manager(object):
    def __init__(self, networkmanager, monitormanager):
        self.networkmanager = networkmanager
        self.monitormanager = monitormanager
    def mainloop(self):
        while True:
            self.networkmanager.check()
            # self.monitormanager.check()