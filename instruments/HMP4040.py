from sys import version_info
if version_info.major == 3:
	from instruments.abstract_instrument import abstract_instrument
else:
	from abstract_instrument import abstract_instrument
import socket

#==============================================================================

ALL_VAL_TYPE = ['VDC - IDC']
ALL_CHANNELS = ['1', '2', '3', '4']

ADDRESS = "10.70.30.60"
CONF_VAL_TYPE = [
	['INST:NSEL i', 'OUTP:SEL ON']]
MEAS_VAL_TYPE = [
	['INST:NSEL i', 'MEAS:VOLT?', 'MEAS:CURR?']]

#==============================================================================

class HMP4040(abstract_instrument):
	def __init__(self, channels, vtypes, address):
		self.address = address
		self.port = 5025
		self.channels = channels
		self.vtypes = vtypes

	def model(self):
		return 'HMP4040'

	def connect(self):
		print('Connecting to device @%s:%s...' %(self.address, self.port))
		self.sock = socket.socket(socket.AF_INET,
							 socket.SOCK_STREAM,
							 socket.IPPROTO_TCP)
		self.sock.settimeout(10.0)	# Don't hang around forever
		self.sock.connect((self.address, self.port))
		print('  --> Ok')
		print(self.model())
		self.configure()

	def configure(self):
		pass

	def getValue(self):
		mes = ''
		for ch in self.channels:
			for command in MEAS_VAL_TYPE[ALL_VAL_TYPE.index(self.vtypes[self.channels.index(ch)])]:
				self.send(command.replace('i', str(ch)))
				if command.endswith('?'):
					mesTemp = self.read()
					mes = mes + '\t' + mesTemp.replace('\n', '')
		return mes + '\n'

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
		self.sock.close()

	def send(self, command):
		self.sock.send(("%s\n"%command).encode())
