from sys import version_info
if version_info.major == 3:
    from instruments.abstract_instrument import abstract_instrument
else:
    from abstract_instrument import abstract_instrument
import socket
import time

#==============================================================================

ALL_VAL_TYPE = ['FREQ']
ALL_CHANNELS = ['1', '2', '3']

ADDRESS = "192.168.0.74"
CONF_VAL_TYPE = ['CONF:FREQ']

#==============================================================================

class AG532x0A(abstract_instrument):
	def __init__(self, channels, vtypes, address):
		self.address = address
		self.port = 5025
		self.channels = channels
		self.vtypes = vtypes

	def model(self):
		return "AG532x0A"

	def connect(self):
		print('Connecting to device @%s:%s...' %(self.address, self.port))
		self.sock = socket.socket(socket.AF_INET,
							 socket.SOCK_STREAM,
							 socket.IPPROTO_TCP)
		self.sock.settimeout(10.0)	# Don't hang around forever
		self.sock.connect((self.address, self.port))
		self.send("SYST:BEEP")
		print('  --> Ok')
		print(self.model())
		self.configure()

	def configure(self):
		self.send('*RST')
		self.send('DISP:DIG:MASK:AUTO OFF')
		self.send('INP%s:IMP 50' %(self.channels[0]))
		self.send('INP%s:COUP AC' %(self.channels[0]))
		self.send('SYST:TIM INF')
		self.send('SENS:ROSC:SOUR EXT')
		self.send('SENS:ROSC:EXT:FREQ 10E6')
		for ch in self.channels:
			self.send(CONF_VAL_TYPE[ALL_VAL_TYPE.index(self.vtypes[self.channels.index(ch)])] + ' (@%s)' %(self.channels[0]))
		self.send('SAMP:COUN 1e6')
		self.send('SENS:FREQ:MODE CONT')
		self.send('SENS:FREQ:GATE:SOUR TIME')
		self.send('SENS:FREQ:GATE:TIME 1')
		self.send('TRIG:SOUR IMM')
		self.send('INIT:IMM')

	def getValue(self):
		mes = ''
		for ch in self.channels:
			self.send('DATA:REM? 1, WAIT')
			mesTemp = self.read()
			mes = mes + '\t' + mesTemp
		return mes

	def read(self):
		ans = ''
		nb_data_list = []
		nb_data = ''
		try:
			while ans != '\n':
				ans = self.sock.recv(1).decode()
				nb_data_list.append(ans) # Return the number of data
			list_size = len(nb_data_list)
			for j in list(range(0, list_size)):
				nb_data = nb_data+nb_data_list[j]
			return nb_data
		except socket.timeout:
			print("Socket timeout error when reading.")
			raise

	def disconnect(self):
		self.send('*RST')
		self.send("SYST:BEEP")
		self.sock.close()

	def send(self, command):
		self.sock.send(("%s\n"%command).encode())
