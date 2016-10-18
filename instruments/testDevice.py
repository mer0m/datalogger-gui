from abstract_instrument import abstract_instrument
import numpy, time

#==============================================================================

ALL_VAL_TYPE = ['vtype', 'DCV', 'ACV', 'DCI', 'ACI', 'RES2W', 'RES4W', 'FREQ']
ALL_CHANNELS = ['0', '1']
ADRESS = "123.456.789.123"

#==============================================================================

class testDevice(abstract_instrument):
    def __init__(self, channels,  vtype, adress = ADRESS):
        self.adress = adress
        self.port = 9999
        self.channels = channels
        print(self.channels)
        self.vtype = vtype
        print(self.vtype)

    def model(self):
        return 'test_device'

    def connect(self):
        print('Connecting to device @%s:%s...' %(self.adress, self.port))
        time.sleep(1)
        print('  --> Ok')

        print(self.model())

    def getValue(self):
        mes = ""
        for ch in self.channels:
            mes = mes + str(numpy.random.rand()) + '\t'
        return mes + '\n'

    def read(self):
        print('reading')
        return 1

    def disconnect(self):
        print('disconnect')

    def send(self, command):
        print('send %s'%command)
