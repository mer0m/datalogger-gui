from abstract_instrument import abstract_instrument
import socket
import time

#==============================================================================

ALL_VAL_TYPE = ['DCV', 'ACV', 'DCI', 'ACI', 'RES2W', 'RES4W', 'FREQ']
ALL_CHANNELS = ['1']

ADDRESS = "192.168.0.61"
CONF_VAL_TYPE = ['CONF:VOLT:DC', 'CONF:VOLT:AC', 'CONF:CURR:DC', 'CONF:CURR:AC', 'CONF:RES', 'CONF:FRES', 'CONF:FREQ']

#==============================================================================

class AG34461A_avg(abstract_instrument):
    def __init__(self, channels, vtypes, address):
        self.address = address
        self.port = 5025
        self.channels = channels
        self.vtypes = vtypes

    def model(self):
        #self.send("*IDN?")
        #return self.read()
        return "AG34461A_avg"

    def connect(self):
        print('Connecting to device @%s:%s...' %(self.address, self.port))
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(10.0)    # Don't hang around forever
        self.sock.connect((self.address, self.port))
        self.send("SYST:BEEP")
        print('  --> Ok')
        print(self.model())
        self.configure()

    def configure(self):
        self.send("*RST")
        for ch in self.channels:
            self.send(CONF_VAL_TYPE[ALL_VAL_TYPE.index(self.vtypes[self.channels.index(ch)])])
        #self.send("CONF:VOLT:DC 1")
        self.send("VOLT:DC:NPLC 10")
        self.send("SAMP:COUN 5")
        self.send("TRIG:COUN 1")
        self.send("TRIG:DEL 0")
        self.send("SENS:ZERO:AUTO OFF")
        self.send("TRIG:SOUR TIM")
        self.send("TRIG:TIM 0.2")
        self.send("INIT")

    def getValue(self):
        mes = ''
        for ch in self.channels:
            self.send("FETC?")
            mesTemp = self.read()
            #print(mesTemp)
            mesTemp = map(float, mesTemp.split(','))
            mes = mes + '\t' + str(sum(mesTemp)/len(mesTemp))
            self.send("INIT")
        mes = mes + '\n'
        return mes

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
        self.send("SYST:BEEP")
        self.sock.close()

    def send(self, command):
        self.sock.send("%s\n"%command)
