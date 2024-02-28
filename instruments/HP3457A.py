from sys import version_info
if version_info.major == 3:
	from instruments.abstract_instrument import abstract_instrument
else:
	from abstract_instrument import abstract_instrument
import socket

#==============================================================================

ALL_VAL_TYPE = ['DCV']
ALL_CHANNELS = ['0', '1', '2', '3']

ADDRESS = "192.168.0.163"
ADDITIONAL_ADDRESS = "10"
CONF_VAL_TYPE = ['DCV']

#==============================================================================

class HP3457A(abstract_instrument):
	def __init__(self, channels, vtypes, address, additional_address):
		self.address = address
		self.port = 1234
		self.gpib_addr = additional_address
		self.channels = channels
		self.vtypes = vtypes

	def model(self):
		return 'HP5457A'

	def connect(self):
		print('Connecting to device @%s:%s GPIB:%s...' %(self.address, self.port, self.gpib_addr))
		self.sock = socket.socket(socket.AF_INET,
							 socket.SOCK_STREAM,
							 socket.IPPROTO_TCP)
		self.sock.settimeout(10.0)	# Don't hang around forever
		self.sock.connect((self.address, self.port))
		self.init_prologix()
		self.send("BEEP")
		print('  --> Ok')
		print(self.model())
		self.configure()

	def configure(self):
		self.send("RESET")
		self.send("CRESET")
		self.send("END ALWAYS")
		self.send("INBUF OFF")
		self.send("BEEP OFF")
		self.send("NPLC .005")
		self.send("TRIG SGL")
		self.send("TERM SCANNER")

	def getValue(self):
		retVal = ''
		for ch in self.channels:
			self.send("CHAN %s"%ch)
			self.send("?")
			retVal = retVal + self.read().replace('\r\n',';')
		retVal = retVal[0:-1] + '\n'
		return retVal

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
		self.send('CRESET')
		self.send('RESET')
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
