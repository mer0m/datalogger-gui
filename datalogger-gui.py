#!/usr/bin/env python3

# -*- coding: utf-8 -*-

import time, os, instruments, inspect, sys, threading
import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtCore import pyqtSlot

#==============================================================================
#==============================================================================

class acq_routine():
	def __init__(self, instrument, channels, vtypes, address, additionalAddress = "", samplingtime = 1, path = os.getcwd(), fileduration = 24*3600, footer = ""):
		try:
			exec('self.instrument = instruments.%s.%s(%s, %s, "%s", "%s")'%(instrument, instrument, channels, vtypes, address, additionalAddress))
		except:
			exec('self.instrument = instruments.%s.%s(%s, %s, "%s")'%(instrument, instrument, channels, vtypes, address))
		self.path = path
		self.samplingtime = samplingtime
		self.fileduration = fileduration
		self.footer = footer

	def makeTree(self):
		try:
			year = time.strftime("%Y", time.gmtime(self.t0))
			month = time.strftime("%Y-%m", time.gmtime(self.t0))
			os.chdir(self.path + '/' + year + '/' + month)
		except:
			try:
				os.chdir(self.path + '/' + year)
				os.mkdir(month)
				os.chdir(self.path + '/' + year + '/' + month)
			except:
				os.chdir(self.path)
				os.mkdir(year)
				os.chdir(self.path + '/' + year)
				os.mkdir(month)
				os.chdir(self.path + '/' + year + '/' + month)

	def connect(self, alreadyConnected = False):
		if alreadyConnected == False:
			self.instrument.connect()

		self.t0 = time.time()
		self.filename = "%s-%s%s.dat"%(time.strftime("%Y%m%d-%H%M%S", time.gmtime(self.t0)), self.instrument.model(), self.footer)
		self.makeTree()
		self.data_file = os.open(self.filename, os.O_RDWR|os.O_CREAT)

	def start(self):
		tic = time.time()

		if (time.time() - self.t0 >= self.fileduration) & (self.fileduration >0 ):
			os.close(self.data_file)
			self.connect(True)

		#epoch time
		epoch = time.time()
		#MJD time
		mjd = epoch / 86400.0 + 40587
		# Meas values
		meas = self.instrument.getValue()
		meas = meas.replace(",", "\t")
		meas = meas.replace(";", "\t")
		meas = meas.replace("+", "")
		meas = meas.replace("E", "e")

		string = "%f\t%f\t%s" % (epoch, mjd, meas)
		string = string.replace("\t\t", "\t")
		os.write(self.data_file, str.encode(string)) # Write in a file
		print(string)

		self.thread = threading.Timer(self.samplingtime - (time.time() - tic), self.start)
		self.thread.start()

	def stop(self):
		self.thread.cancel()
		self.instrument.disconnect()
		os.close(self.data_file)

#==============================================================================
#==============================================================================

class mainGui():
	def __init__(self):
		self.setWindow()
		self.setSignalsSlots()
		self.runApp()

	def setWindow(self):
		self.a = QtWidgets.QApplication(sys.argv)
		self.w = QtWidgets.QMainWindow()
		self.w.resize(640, 480)
		self.w.setWindowTitle('datalogger-gui')

		self.wid = QtWidgets.QWidget()
		self.w.setCentralWidget(self.wid)
		self.layout = QtWidgets.QGridLayout()
		self.wid.setLayout(self.layout)

		self.comboInst = QtWidgets.QComboBox()
		self.comboInst.setToolTip("List of available instruments")
		self.layout.addWidget(self.comboInst, 0, 0)

		self.address = QtWidgets.QLineEdit()
		self.address.setToolTip("IP/USB address")
		self.address.setMinimumWidth(240)
		self.address.setMaximumWidth(240)
		self.layout.addWidget(self.address, 1, 0)

		self.samplingtime = QtWidgets.QDoubleSpinBox()
		self.samplingtime.setToolTip("Sampling period (s)")
		self.samplingtime.setMinimumWidth(100)
		self.samplingtime.setMaximumWidth(100)
		self.samplingtime.setMinimum(0.1)
		self.samplingtime.setMaximum(1000)
		self.samplingtime.setSingleStep(0.1)
		self.samplingtime.setValue(1)
		self.layout.addWidget(self.samplingtime, 0, 1)

		self.footer = QtWidgets.QLineEdit()
		self.footer.setText("footer")
		self.footer.setToolTip("Filename footer")
		self.footer.setMinimumWidth(240)
		self.footer.setMaximumWidth(240)
		self.layout.addWidget(self.footer, 2, 0)

		self.checkBoxFooter = QtWidgets.QCheckBox()
		self.checkBoxFooter.setToolTip("Use custom filename footer")
		self.checkBoxFooter.setText("Footer")
		self.checkBoxFooter.setChecked(False)
		self.layout.addWidget(self.checkBoxFooter, 2, 1)

		self.startStopLayout = QtWidgets.QHBoxLayout()

		self.startButton = QtWidgets.QPushButton()
		self.startButton.setToolTip("When you're sure of your settings !")
		self.startButton.setText('Start log')
		self.startStopLayout.addWidget(self.startButton)
		self.startButton.setEnabled(False)

		self.stopButton = QtWidgets.QPushButton()
		self.stopButton.setToolTip("Why ? Too much disturbances ?")
		self.stopButton.setText('Stop log')
		self.startStopLayout.addWidget(self.stopButton)
		self.stopButton.setEnabled(False)

		self.layout.addLayout(self.startStopLayout, 0, 2)

		self.prompt = QtWidgets.QStatusBar()
		self.prompt.setToolTip("Command summary")
		self.prompt.showMessage('>>')
		self.w.setStatusBar(self.prompt)

		self.setComboInst()
		self.makeCurrentInstrumentGui()

	def setComboInst(self):
		for name, obj in inspect.getmembers(instruments):
			if inspect.ismodule(obj) and name.startswith('__') == False and name.startswith('abstract') == False:
				self.comboInst.addItem(name)

	def setSignalsSlots(self):
		self.comboInst.currentIndexChanged.connect(self.makeCurrentInstrumentGui)
		self.startButton.clicked.connect(self.startLog)
		self.stopButton.clicked.connect(self.stopLog)

	def runApp(self):
		self.w.show()
		self.a.aboutToQuit.connect(self.closeEvent)
		sys.exit(self.a.exec_())

	def closeEvent(self):
		try:
			self.stopLog()
		except:
			pass
		print('Done')

	#@pyqtSlot()
	def makeCurrentInstrumentGui(self):
		for i in reversed(list(range(5, self.layout.count()))):
			try:
				self.layout.itemAt(i).widget().setParent(None)
			except:
				pass

		defaultAddress = ''
		channelsAviables = []
		vtypesAviables = []
		additionalAddress = ''

		try:
			channelsAviables = eval('instruments.%s.ALL_CHANNELS'%self.comboInst.currentText())
		except:
			pass
		try:
			vtypesAviables = eval('instruments.%s.ALL_VAL_TYPE'%self.comboInst.currentText())
		except:
			pass
		try:
			defaultAddress = eval('instruments.%s.ADDRESS'%self.comboInst.currentText())
		except:
			pass
		try:
			additionalAddress = eval('instruments.%s.ADDITIONAL_ADDRESS'%self.comboInst.currentText())
		except:
			pass

		self.address.setText(defaultAddress)

		if additionalAddress != '':
			self.addAddress = QtWidgets.QLineEdit()
			self.addAddress.setToolTip("GPIB address/...")
			self.addAddress.setMinimumWidth(100)
			self.addAddress.setMaximumWidth(100)
			self.layout.addWidget(self.addAddress, 1, 1)

			self.addAddress.setText(additionalAddress)
			self.addAddress.textChanged.connect(self.setCurrentInstConf)
		else:
			try:
				del(self.addAddress)
			except:
				pass

		self.checkBoxChannels = [None]*len(channelsAviables)
		self.chListVtypes = [None]*len(self.checkBoxChannels)

		for i in range(len(self.checkBoxChannels)):
			self.checkBoxChannels[i] = QtWidgets.QCheckBox()
			self.checkBoxChannels[i].setToolTip("Channel %s"%channelsAviables[i])
			self.checkBoxChannels[i].setText(channelsAviables[i])
			self.checkBoxChannels[i].setChecked(False)
			self.chListVtypes[i] = QtWidgets.QListWidget()
			self.chListVtypes[i].setToolTip("Select type of measure")
			for vtype in vtypesAviables:
				self.chListVtypes[i].addItem(vtype)
			self.chListVtypes[i].setCurrentRow(0)
			self.layout.addWidget(self.checkBoxChannels[i], i+10, 1)
			self.layout.addWidget(self.chListVtypes[i], i+10, 2)
			self.checkBoxChannels[i].stateChanged.connect(self.setCurrentInstConf)
			self.chListVtypes[i].currentItemChanged.connect(self.setCurrentInstConf)

		self.address.textChanged.connect(self.setCurrentInstConf)
		self.samplingtime.valueChanged.connect(self.setCurrentInstConf)
		self.checkBoxFooter.stateChanged.connect(self.setCurrentInstConf)
		self.footer.textChanged.connect(self.setCurrentInstConf)

		self.setCurrentInstConf()

	#@pyqtSlot()
	def setCurrentInstConf(self):
		self.instToLog = self.comboInst.currentText()
		self.addressToLog = self.address.text()
		try:
			self.additional_address = self.addAddress.text()
		except:
			try:
				del(self.additional_address)
			except:
				pass
		self.chToLog = []
		self.vTypeToLog = []
		self.ts = self.samplingtime.value()
		if self.checkBoxFooter.isChecked():
			self.filenameFooter = "_%s"%self.footer.text()
			self.footer.setEnabled(True)
		else:
			self.filenameFooter = ""
			self.footer.setEnabled(False)

		for i in range(len(self.checkBoxChannels)):
			if self.checkBoxChannels[i].isChecked():
				self.chListVtypes[i].setEnabled(True)
				self.chToLog.append(str(self.checkBoxChannels[i].text()))
				self.vTypeToLog.append(str(self.chListVtypes[i].currentItem().text()))
			else:
				self.chListVtypes[i].setEnabled(False)

		allChannelsUnchecked = False
		for i in self.checkBoxChannels:
			allChannelsUnchecked = allChannelsUnchecked or i.isChecked()
		if allChannelsUnchecked == False:
			self.startButton.setEnabled(False)
		else:
			self.startButton.setEnabled(True)

		try:
			promptStr = ">> %s%s@%s:%s - %s - %s - %d"%(self.instToLog,
				self.filenameFooter,
				self.addressToLog,
				self.additional_address,
				self.chToLog,
				self.vTypeToLog,
				self.ts)
			self.myLog = acq_routine(instrument = self.instToLog,
				channels = self.chToLog,
				vtypes = self.vTypeToLog,
				address = self.addressToLog,
				additionalAddress = self.additional_address,
				samplingtime = self.ts,
				footer = self.filenameFooter)
		except:
			promptStr = ">> %s%s@%s - %s - %s - %d"%(self.instToLog,
				self.filenameFooter,
				self.addressToLog,
				self.chToLog,
				self.vTypeToLog,
				self.ts)
			self.myLog = acq_routine(instrument = self.instToLog,
				channels = self.chToLog,
				vtypes = self.vTypeToLog,
				address = self.addressToLog,
				samplingtime = self.ts,
				footer = self.filenameFooter)

		self.prompt.showMessage(promptStr)

	#@pyqtSlot()
	def startLog(self):
		self.startButton.setEnabled(False)
		self.stopButton.setEnabled(True)
		self.address.setEnabled(False)
		try:
			self.addAddress.setEnabled(False)
		except:
			pass
		self.samplingtime.setReadOnly(True)
		self.checkBoxFooter.setEnabled(False)
		self.footer.setEnabled(False)
		self.comboInst.setEnabled(False)
		for i in self.checkBoxChannels:
			i.setEnabled(False)
		for i in self.chListVtypes:
			i.setEnabled(False)
		self.myLog.connect()
		self.myLog.start()

	#@pyqtSlot()
	def stopLog(self):
		self.startButton.setEnabled(True)
		self.stopButton.setEnabled(False)
		self.address.setEnabled(True)
		try:
			self.addAddress.setEnabled(True)
		except:
			pass
		self.samplingtime.setReadOnly(False)
		self.checkBoxFooter.setEnabled(True)
		if self.checkBoxFooter.isChecked():
			self.footer.setEnabled(True)
		else:
			self.footer.setEnabled(False)
		self.comboInst.setEnabled(True)
		for i in range(len(self.checkBoxChannels)):
			if self.checkBoxChannels[i].isChecked():
				self.checkBoxChannels[i].setEnabled(True)
				self.chListVtypes[i].setEnabled(True)
			else:
				self.checkBoxChannels[i].setEnabled(True)
				self.chListVtypes[i].setEnabled(False)
		self.myLog.stop()

#==============================================================================
#==============================================================================

if __name__ == "__main__":
	mainGui()
