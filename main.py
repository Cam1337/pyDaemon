from pydaemon.manager import Manager, NetworkManager
from pydaemon.connection import RemoteSocket
from pydaemon.protocol import sd_proto

rs = RemoteSocket("anon.so",10000,(None, None), sd_proto)
nm = NetworkManager([rs])
dm = Manager(nm, None)
dm.mainloop()