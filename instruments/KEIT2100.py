from sys import version_info
if version_info.major == 3:
    from instruments.abstract_instrument import abstract_instrument
else:
    from abstract_instrument import abstract_instrument
import os

#==============================================================================

ALL_VAL_TYPE = ['DCV', 'ACV', 'DCI', 'ACI', 'RES']
ALL_CHANNELS = ['1']

ADDRESS = "/dev/usbtmc0"
CONF_VAL_TYPE_QUER = ['MEAS:VOLT:DC?', 'MEAS:VOLT:AC?', 'MEAS:CURR:DC?', 'MEAS:CURR:AC', 'MEAS:RES?', 'MEAS:TEMP?']

#==============================================================================

class KEIT2100(abstract_instrument):
	def __init__(self, channels, vtypes, address, additional_address):
		self.address = address
		self.channels = channels
		self.vtypes = vtypes

	def model(self):
		return 'KEIT2100'

	def connect(self):
		print('Connecting to device @%s...' %(self.address))
		self.FILE = os.open(self.address, os.O_RDWR)
		print('  --> Ok')
		print(self.model())
		self.configure()

	def configure(self):
		self.send('*RST')
		self.send('*CLS')
		self.send('CALC:DEM:REF 50')
		self.send('SAMP:COUN 1') ##COUT
		for ch in self.channels:
			self.send(CONF_VAL_TYPE_QUER[ALL_VAL_TYPE.index(self.vtypes[self.channels.index(ch)])])

	def getValue(self):
		self.send('READ?')
		mesTemp = self.read().decode()
		mes = mesTemp.replace('E', 'e').replace('+','') + '\n'
		return mes

	def read(self):
		return os.read(self.FILE, 300)

	def disconnect(self):
		self.send('*RST')

	def send(self, command):
		os.write(self.FILE, command.encode())
