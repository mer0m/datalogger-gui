from abstract_instrument import abstract_instrument
import socket

#==============================================================================

ALL_VAL_TYPE = ['DCV', 'ACV', 'DCI', 'ACI', 'RES2W', 'RES4W', 'FREQ']
ALL_CHANNELS = ['101', '102', '103', '104', '105']

ADRESS = "192.168.0.72"
CONF_VAL_TYPE = ['CONF:VOLT:DC', 'CONF:VOLT:AC', 'CONF:CURR:DC', 'CONF:CURR:AC', 'CONF:RES', 'CONF:FRES', 'CONF:FREQ']

#==============================================================================

class AG34972A(abstract_instrument):
    def __init__(self, channels, vtypes, adress):
        self.adress = adress
        self.port = 5025
	self.channels = channels
        self.vtypes = vtypes

    def model(self):
        #self.send("*IDN?")
        #return self.read()
	return "AG34972A"

    def connect(self):
        print('Connecting to device @%s:%s...' %(self.adress, self.port))
        self.sock = socket.socket(socket.AF_INET,
                             socket.SOCK_STREAM,
                             socket.IPPROTO_TCP)
        self.sock.settimeout(2.0)    # Don't hang around forever
        self.sock.connect((self.adress, self.port))
        self.send("SYST:BEEP")
        print('  --> Ok')
        print(self.model())
        self.configure()

    def configure(self):
        self.strCh = ''
	for ch in self.channels:
            self.send('%s (@%s)'%(CONF_VAL_TYPE[ALL_VAL_TYPE.index(self.vtypes[self.channels.index(ch)])], ch))
	    self.strCh = self.strCh + ch + ','
	self.strCh = self.strCh[0:-1]
	self.send("ROUT:SCAN (@%s)"%self.strCh)                                                                      
        self.send("TRIG:COUN 1") 

    def getValue(self):
        self.send("INIT")
	self.send("FETC?")
        return self.read()

    def read(self):
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
        self.send('*RST')
        self.sock.close()

    def send(self, command):
        self.sock.send("%s\n"%command)
