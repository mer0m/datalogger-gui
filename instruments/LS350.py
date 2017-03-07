from abstract_instrument import abstract_instrument
import socket

#==============================================================================

ALL_VAL_TYPE = ['TEMP', 'RES']
ALL_CHANNELS = ['a', 'b', 'c', 'd']

ADDRESS = "192.168.0.12"
CONF_VAL_TYPE = ['krdg?', 'srdg?']

#==============================================================================

class LS350(abstract_instrument):
    def __init__(self, channels, vtypes, address):
        self.address = address
        self.port = 7777
        self.channels = channels
        self.vtypes = vtypes

    def model(self):
        #self.send("*IDN?")
        #return self.read()
        return "LS350"

    def connect(self):
        print('Connecting to device @%s:%s...' %(self.address, self.port))
        self.sock = socket.socket(socket.AF_INET,
                             socket.SOCK_STREAM,
                             socket.IPPROTO_TCP)
        self.sock.settimeout(10.0)    # Don't hang around forever
        self.sock.connect((self.address, self.port))
        print('  --> Ok')
        print(self.model())
        self.configure()

    def configure(self):
        self.strCh = ''
        for ch in self.channels:
            self.strCh = self.strCh + '%s %s;'%(CONF_VAL_TYPE[ALL_VAL_TYPE.index(self.vtypes[self.channels.index(ch)])], ch)
        self.strCh = self.strCh[0:-1]
        print(self.strCh)

    def getValue(self):
        self.send(self.strCh)
        return self.read()

    def read(self):
        self.send("++read eoi")
        ans = ''
        nb_data_list = []
        nb_data = ''
        try:
            while ans != '\n':
                ans = self.sock.recv(1)
                nb_data_list.append(ans) # Return the number of data
            list_size = len(nb_data_list)
            for j in range (0, list_size):
                nb_data = nb_data+nb_data_list[j]
            return nb_data
        except socket.timeout:
            print "Socket timeout error when reading."
            raise

    def disconnect(self):
        self.send('MODE0')
        self.sock.close()

    def send(self, command):
        self.sock.send("%s\n"%command)
