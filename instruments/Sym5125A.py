from sys import version_info
if version_info.major == 3:
    from instruments.abstract_instrument import abstract_instrument
else:
    from abstract_instrument import abstract_instrument
import telnetlib, time

#==============================================================================

ALL_VAL_TYPE = ['phase']
ALL_CHANNELS = ['1']

ADDRESS = "192.168.0.222"
CONF_VAL_TYPE = ['phase']

#==============================================================================

class Sym5125A(abstract_instrument):
	def __init__(self, channels, vtypes, address):
		self.address = address
		self.channels = channels
		self.vtypes = vtypes

	def model(self):
		return "Sym5125A"

	def connect(self):
		print('Connecting to device @%s...' %(self.address))
		self.tn = telnetlib.Telnet(self.address, '1298')
		print('  --> Ok')
		print(self.model())
		self.configure()

	def configure(self):
		print('No channel to configure')
		pass

	def getValue(self):
		for i in list(range(1000)):
			mes = self.tn.read_until('\n'.encode()).replace('\r\n','')
		return mes + '\n'

	def read(self):
		pass

	def disconnect(self):
		self.tn.close()

	def send(self, command):
		pass
