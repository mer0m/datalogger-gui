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
		#self.send("*IDN?")
		#return self.read()
		return "Sym5125A"

	def connect(self):
		print('Connecting to device @%s...' %(self.address))
		self.tn = telnetlib.Telnet(self.address, '1298')
		#time.sleep(1)
		print('  --> Ok')
		print(self.model())
		self.configure()

	def configure(self):
		pass

	def getValue(self):
		for i in range(1000):
			mes = self.tn.read_until('\n').replace('\r\n','')
		return mes + '\n'

	def read(self):
		pass

	def disconnect(self):
		self.tn.close()

	def send(self, command):
		pass
