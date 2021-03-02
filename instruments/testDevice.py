from sys import version_info
if version_info.major == 3:
    from instruments.abstract_instrument import abstract_instrument
else:
    from abstract_instrument import abstract_instrument
import numpy, time

#==============================================================================

ALL_VAL_TYPE = ['vtype', 'DCV', 'ACV', 'DCI', 'ACI', 'RES2W', 'RES4W', 'FREQ']
ALL_CHANNELS = ['0', '1']
ADDRESS = "123.456.789.123"
ADDITIONAL_ADDRESS = "1"

#==============================================================================

class testDevice(abstract_instrument):
	def __init__(self, channels,  vtype, address, additional_address):
		self.address = address
		self.port = 9999
		self.additional_addr = additional_address
		self.channels = channels
		self.vtype = vtype

	def model(self):
		return 'test_device'

	def connect(self):
		print('Connecting to device @%s:%s - %s...' %(self.address, self.port, self.additional_addr))
		time.sleep(1)
		print('  --> Ok')
		self.configure()

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

	def configure(self):
		print(self.channels)
		print(self.vtype)
		print('configured')
