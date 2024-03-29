from sys import version_info
if version_info.major == 3:
	from instruments.abstract_instrument import abstract_instrument
else:
	from abstract_instrument import abstract_instrument
import socket

#==============================================================================

ALL_VAL_TYPE = ['DCV', 'ACV', 'DCI', 'ACI', 'RES']
ALL_CHANNELS = ['1']

ADDRESS = "10.1.28.59"
ADDITIONAL_ADDRESS = "7"
CONF_VAL_TYPE = ['F0DX', 'F1DX', 'F3DX', 'F4DX', 'F2DX']

#==============================================================================

class KEIT196(abstract_instrument):
	def __init__(self, channels, vtypes, address, additional_address):
		self.address = address
		self.port = 1234
		self.gpib_addr = additional_address
		self.channels = channels
		self.vtypes = vtypes

	def model(self):
		return 'KEIT196'

	def connect(self):
		print('Connecting to device @%s:%s GPIB:%s...' %(self.address, self.port, self.gpib_addr))
		self.sock = socket.socket(socket.AF_INET,
							 socket.SOCK_STREAM,
							 socket.IPPROTO_TCP)
		self.sock.settimeout(10.0)	# Don't hang around forever
		self.sock.connect((self.address, self.port))
		self.init_prologix()
		print('  --> Ok')
		print(self.model())
		self.configure()

	def configure(self):
		self.send('*RST')
		for ch in self.channels:
			self.send(CONF_VAL_TYPE[ALL_VAL_TYPE.index(self.vtypes[self.channels.index(ch)])])
		self.send('YX')
		self.send('G1DX')
		self.send('R0DX')
		self.send('W100') #delay in milliseconds 0ms -> 6000ms

	def getValue(self):
		#self.send('FETC?')
		#self.send('READ:FREQ?')
		return self.read()

	def read(self):
		self.send("++read eoi")
		ans = ''
		nb_data_list = []
		nb_data = ''
		try:
			while ans != '\n':
				ans = self.sock.recv(1).decode()
				nb_data_list.append(ans) # Return the number of data
			list_size = len(nb_data_list)
			for j in range (0, list_size):
				nb_data = nb_data+nb_data_list[j]
			if type(nb_data) == type(b'0'):
				return nb_data.decode()
			else:
				return nb_data
		except socket.timeout:
			print("Socket timeout error when reading.")
			raise

	def disconnect(self):
		self.send('*RST')
		self.sock.close()

	def send(self, command):
		self.sock.send(("%s\n"%command).encode())

	def init_prologix(self):
		try:
			self.sock.send(("++mode 1\n").encode()) # Set mode as CONTROLLER
			self.sock.send(("++addr %s\n"%self.gpib_addr).encode()) # Set the GPIB address
			self.sock.send(("++eos 3\n").encode()) # Set end-of-send character to nothing
			self.sock.send(("++eoi 1\n").encode()) # Assert EOI with last byte to indicate end
			self.sock.send(("++read_tmo_ms 2750\n").encode()) # Set read timeout
			self.sock.send(("++auto 0\n").encode()) # Turn off read-after-write to avoid

		except self.socket.timeout:
			print("Socket timeout")
			raise
		except self.socket.error as er:
			print("Socket error: %s"%er)
			raise
		except Exception as er:
			print("Unexpected error: %s"%er)
			raise
