from abstract_instrument import abstract_instrument
import os

#==============================================================================

ALL_VAL_TYPE = ['PWR']
ALL_CHANNELS = ['1']

ADDRESS = "/dev/usbtmc0"
CONF_VAL_TYPE = ['PWR']

#==============================================================================

class PM100D(abstract_instrument):
    def __init__(self, channels, vtypes, address):
        self.address = address
        self.channels = channels
        self.vtypes = vtypes

    def model(self):
        #self.send("*IDN?")
        #return self.read()
        return "PM100D"

    def connect(self):
        print('Connecting to device @%s...' %(self.address))
        self.FILE = os.open(self.address, os.O_RDWR)
        print('  --> Ok')
        print(self.model())
        self.configure()

    def configure(self):
        pass

    def getValue(self):
        self.send("READ?")
        return self.read()

    def read(self):
        return os.read(self.FILE, 300)

    def disconnect(self):
        self.send('*RST')

    def send(self, command):
        os.write(self.FILE, command)
