from abstract_instrument import abstract_instrument
from labjack import ljm
import numpy

#==============================================================================

ALL_VAL_TYPE = ['RES', 'TEMP PT100 K', 'TEMP PT100 C', 'TEMP AIR K']
ALL_CHANNELS = ['1', '2', '3', '4', 'TEMP AIR K']

ADDRESS = "192.168.0.25"
CONF_CHANNELS = [["AIN0", "AIN10"], ["AIN2", "AIN11"], ["AIN4", "AIN12"], ["AIN6", "AIN13"], ["TEMPERATURE_AIR_K"]]
VISHAY_CHANNELS = [1000., 1000., 1079., 10000.]

#==============================================================================

class T7Pro(abstract_instrument):
	def __init__(self, channels, vtypes, address):
		self.address = address
		self.channels = channels
		self.vtypes = vtypes

	def model(self):
		return 'T7Pro'

	def connect(self):
		print('Connecting to device @%s...' %(self.address))
		self.handle = ljm.openS("T7", "ETHERNET", self.address)
		print('  --> Ok')
		print(self.model())
		self.configure()

	def configure(self):
		names = ["AIN0_NEGATIVE_CH", "AIN0_RANGE", "AIN0_RESOLUTION_INDEX",
				"AIN1_NEGATIVE_CH", "AIN1_RANGE", "AIN1_RESOLUTION_INDEX",
				"AIN2_NEGATIVE_CH", "AIN2_RANGE", "AIN2_RESOLUTION_INDEX",
				"AIN3_NEGATIVE_CH", "AIN3_RANGE", "AIN3_RESOLUTION_INDEX",
				"AIN4_NEGATIVE_CH", "AIN4_RANGE", "AIN4_RESOLUTION_INDEX",
				"AIN5_NEGATIVE_CH", "AIN5_RANGE", "AIN5_RESOLUTION_INDEX",
				"AIN6_NEGATIVE_CH", "AIN6_RANGE", "AIN6_RESOLUTION_INDEX",
				"AIN7_NEGATIVE_CH", "AIN7_RANGE", "AIN7_RESOLUTION_INDEX",
				#"AIN8_NEGATIVE_CH", "AIN8_RANGE", "AIN8_RESOLUTION_INDEX",
				#"AIN9_NEGATIVE_CH", "AIN9_RANGE", "AIN9_RESOLUTION_INDEX",
				"AIN10_NEGATIVE_CH", "AIN10_RANGE", "AIN10_RESOLUTION_INDEX",
				"AIN11_NEGATIVE_CH", "AIN11_RANGE", "AIN11_RESOLUTION_INDEX",
				"AIN12_NEGATIVE_CH", "AIN12_RANGE", "AIN12_RESOLUTION_INDEX",
				"AIN13_NEGATIVE_CH", "AIN13_RANGE", "AIN13_RESOLUTION_INDEX"
				]
		l_names = len(names)
		aValues = [1, 1, 12,#0
				199, 1, 12,#1
				3, 1, 12,#2
				199, 1, 12,#3
				5, 1, 12,#4
				199, 1, 12,#5
				7, 1, 12,#6
				199, 1, 12,#7
				#199, 1, 12,#8
				#199, 1, 12,#9
				199, 1, 12,#10
				199, 1, 12,#11
				199, 1, 12,#12
				199, 1, 12#13
				]

		ljm.eWriteNames(self.handle, l_names, names, aValues)

	def getValue(self):
		strMes = ''
		for ch in self.channels:
			if self.vtypes[self.channels.index(ch)] == 'RES':
				raw = self.read(CONF_CHANNELS[ALL_CHANNELS.index(ch)])
				strMes = strMes + str(VISHAY_CHANNELS[ALL_CHANNELS.index(ch)]*raw[0]/raw[1]) + ';'
			elif self.vtypes[self.channels.index(ch)] == 'TEMP PT100 K':
				raw = self.read(CONF_CHANNELS[ALL_CHANNELS.index(ch)])
				strMes = strMes + str(((VISHAY_CHANNELS[ALL_CHANNELS.index(ch)]*raw[0]/raw[1])/100.-1)/0.003850+273.15) + ';'
			elif self.vtypes[self.channels.index(ch)] == 'TEMP PT100 C':
				raw = self.read(CONF_CHANNELS[ALL_CHANNELS.index(ch)])
				strMes = strMes + str(((VISHAY_CHANNELS[ALL_CHANNELS.index(ch)]*raw[0]/raw[1])/100.-1)/0.003850) + ';'
			elif self.vtypes[self.channels.index(ch)] == 'TEMP AIR K':
				raw = self.read(CONF_CHANNELS[ALL_CHANNELS.index(ch)])
				strMes = strMes + str(raw[0]) + ';'

		strMes = strMes[0:-1] + '\n'
		return(strMes)

	def read(self, names):
		return ljm.eReadNames(self.handle, len(names), names)

	def disconnect(self):
		ljm.close(self.handle)

	def send(self, command):
		pass
