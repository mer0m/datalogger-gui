from abstract_instrument import abstract_instrument
from labjack import ljm
import numpy

#==============================================================================

ALL_VAL_TYPE = ['TEMP', 'RES']
ALL_CHANNELS = ['TEMP', '1', '2', '3', '4']
ADRESS = "192.168.0.25"

#==============================================================================

class T7Pro(abstract_instrument):
    def __init__(self, adress=ADRESS, vtype=[ALL_VAL_TYPE[0]], channels = [ALL_CHANNELS[0]]):
	self.adress = adress
	self.vtype = vtype
	self.tempName = ["TEMPERATURE_AIR_K"]
	self.res1Name = ["AIN0", "AIN10"]
	self.res2Name = ["AIN2", "AIN11"]
	self.res3Name = ["AIN4", "AIN12"]
	self.res4Name = ["AIN6", "AIN13"]

    def model(self):
        return 'T7Pro'

    def connect(self):
        try:
            print('Connecting to device @%s...' %(self.adress))
            self.handle = ljm.openS("T7", "ETHERNET", self.adress)
            self.configureAINs()
            print('  --> Ok')

            print(self.model())

            if self.vtype == "TEMP":
                1
            elif self.vtype == "RES":
                1
            else:
                print("Wrong -v argument")
                raise

        except Exception as er:
            print("Unexpected error during connection: " + str(er))
            raise

    def getValue(self):
        mesTemp = self.read(self.tempName)
	mesRes1 = self.read(self.res1Name)
	mesRes2 = self.read(self.res2Name)
	mesRes3 = self.read(self.res3Name)
	mesRes4 = self.read(self.res4Name)
#	mesRes4 = [1, 1]
#	print("~~~~~~~~~~~~~~~~~~~~~~\n" + str(results) + "~~~~~~~~~~~~~~~~~~~~~~\n")
        temp = mesTemp[0]
        res1 = 100.*mesRes1[0]/mesRes1[1]
	res2 = 100.*mesRes2[0]/mesRes2[1]
	res3 = 100.*mesRes3[0]/mesRes3[1]
	res4 = 100.*mesRes4[0]/mesRes4[1]

        if self.vtype == 'TEMP':
            # Temperature calculation
            temp1 = self.res2tempSensor(628, res1)
            temp2 = self.res2tempSensor(16947, res2)
            temp3 = self.res2tempSensor(625, res3)
            temp4 = self.res2tempSensor(100, res4)
            string = '%f\t%f\t%f\t%f\t%f\n'%(temp, temp1, temp2, temp3, temp4)
#	    string = '%f\t%f\n'%(temp, temp1)
        elif self.vtype == 'RES':
            string = '%f\t%f\t%f\t%f\t%f\n'%(temp, res1, res2, res3, res4)
#	    string = '%f\t%f\n'%(temp, res1)
        else:
            string = ''

        return string

    def read(self, names):
        return ljm.eReadNames(self.handle, len(names), names)

    def disconnect(self):
        ljm.close(self.handle)

    def send(self, command):
        pass

    def configureAINs(self):
    # Setup and call eWriteNames to configure AINs on the LabJack.
        names = ["AIN0_NEGATIVE_CH", "AIN0_RANGE", "AIN0_RESOLUTION_INDEX",
         "AIN1_NEGATIVE_CH", "AIN1_RANGE", "AIN1_RESOLUTION_INDEX",
         "AIN2_NEGATIVE_CH", "AIN2_RANGE", "AIN2_RESOLUTION_INDEX",
         "AIN3_NEGATIVE_CH", "AIN3_RANGE", "AIN3_RESOLUTION_INDEX",
	 "AIN4_NEGATIVE_CH", "AIN4_RANGE", "AIN4_RESOLUTION_INDEX",
         "AIN5_NEGATIVE_CH", "AIN5_RANGE", "AIN5_RESOLUTION_INDEX",
         "AIN6_NEGATIVE_CH", "AIN6_RANGE", "AIN6_RESOLUTION_INDEX",
         "AIN7_NEGATIVE_CH", "AIN7_RANGE", "AIN7_RESOLUTION_INDEX",
	 "AIN8_NEGATIVE_CH", "AIN8_RANGE", "AIN8_RESOLUTION_INDEX",
         "AIN9_NEGATIVE_CH", "AIN9_RANGE", "AIN9_RESOLUTION_INDEX",
         "AIN10_NEGATIVE_CH", "AIN10_RANGE", "AIN10_RESOLUTION_INDEX",
	 "AIN11_NEGATIVE_CH", "AIN11_RANGE", "AIN11_RESOLUTION_INDEX",
	 "AIN12_NEGATIVE_CH", "AIN12_RANGE", "AIN12_RESOLUTION_INDEX",
	 "AIN13_NEGATIVE_CH", "AIN13_RANGE", "AIN13_RESOLUTION_INDEX"
         ]
        l_names = len(names)
        aValues = [1, 0.1, 12,#0
		   199, 0.1, 12,#1
                   3, 0.1, 12,#2
                   199, 0.1, 12,#3
                   5, 0.1, 12,#4
                   199, 0.1, 12,#5
                   7, 0.1, 12,#6
                   199, 0.1, 12,#7
                   199, 0.1, 12,#8
		   199, 0.1, 12,#9
		   199, 0.1, 12,#10
		   199, 0.1, 12,#11
                   199, 0.1, 12,#12
		   199, 0.1, 12#13
                   ]
        ljm.eWriteNames(self.handle, l_names, names, aValues)


    def res2tempSensor(self, sensor, res):
        if sensor==627:
            K = [0.399341181655472610,
                 10.8420092277810909,
                 -26.4597939187660813,
                 245.9828566655493379,
                 -668.069876596331596,
                 1001.69882618263364,
                 -267.272089680656791]
        if sensor==625:
            K = [0.333548856582638109,
                 11.7361551595386118,
                 -31.32988932320903987,
                 262.878643524833024,
                 -704.163538021035492,
                 1056.6040485650301,
                 -307.057196729816496]
        if sensor==628:
            K = [0.463200932294057566,
                 13.5049710820894688,
                 -30.5191222755238414,
                 231.098593852017075,
                 -550.122691885568202,
                 806.038547554984689,
                 -198.510489917360246]
        if sensor==16945:
            K = [3.2497, 5.1777, 2.499]
        if sensor==16943:
            K = [3.4738, 5.1198, 2.3681]
        if sensor==16944:
            K = [3.3674, 5.2874, 2.5165]
        if sensor==16941:
            K = [2.9486, 4.5862, 2.266]
        if sensor==16947:
            K = [3.4597, 5.2422, 2.4169]
        if sensor==100:
            K = [0.003850]
        return self.res2temp(K, res)

    def res2temp(K, res):
        temp = 0
        tmp = 1000./res
        if len(K)==7:
            for i in range(len(K)):
                temp += K[i]*tmp**i
        if len(K)==3:
            for i in range(len(K)):
                temp += K[i]*numpy.log10(tmp)**(2-i)
            temp = 10**temp
        if len(K)==1:
            temp = (res/100.-1)/K[0]+273.15
        return temp
