#!/usr/bin/env python

# -*- coding: utf-8 -*-

import time, os, instruments, inspect, sys, threading
import PyQt4.QtGui as QtGui
from PyQt4.QtCore import pyqtSlot

#==============================================================================
#==============================================================================

class acq_routine():
    def __init__(self, instrument, channels, vtypes, address, path = os.getcwd(), samplingtime = 1, fileduration = 24*3600):
        exec('self.instrument = instruments.%s.%s(%s, %s, "%s")'%(instrument, instrument, channels, vtypes, address))
        self.path = path
        self.samplingtime = samplingtime
        self.fileduration = fileduration

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

    def connect(self):
        self.instrument.connect()

        self.t0 = time.time()
        self.filename = time.strftime("%Y%m%d-%H%M%S", time.gmtime(self.t0)) + '-' + self.instrument.model() + '.dat'
        self.makeTree()
        self.data_file = open(self.filename, 'wr', 0)

    def start(self):
        tic = time.time()

        if (time.time() - self.t0 >= self.fileduration) & (self.fileduration >0 ):
            self.data_file.close()

            self.t0 = time.time()
            self.filename = time.strftime("%Y%m%d-%H%M%S", time.gmtime(self.t0)) + '-' + self.instrument.model() + '.dat'
            self.makeTree()
            self.data_file = open(self.filename, 'wr', 0)

        #epoch time
        epoch = time.time()
        #MJD time
        mjd = epoch / 86400.0 + 40587
        # Meas values
        meas = self.instrument.getValue()
        meas = meas.replace(",", "\t")
        meas = meas.replace(";", "\t")
        meas = meas.replace("+", "")

        string = "%f\t%f\t%s" % (epoch, mjd, meas)
        self.data_file.write(string) # Write in a file
        print(string)

        self.thread = threading.Timer(self.samplingtime - (time.time() - tic), self.start)
        self.thread.start()

    def stop(self):
        self.thread.cancel()
        self.instrument.disconnect()
        self.data_file.close()

#==============================================================================
#==============================================================================

class mainGui():
    def __init__(self):
        self.setWindow()
        self.setSignalsSlots()
        self.runApp()

    def setWindow(self):
        self.a = QtGui.QApplication(sys.argv)
        self.w = QtGui.QMainWindow()
        self.w.resize(640, 480)
        self.w.setWindowTitle('datalogger-gui')

        self.wid = QtGui.QWidget()
        self.w.setCentralWidget(self.wid)
        self.layout = QtGui.QGridLayout()
        self.wid.setLayout(self.layout)

        self.comboInst = QtGui.QComboBox()
        self.layout.addWidget(self.comboInst, 0, 0)

        self.address = QtGui.QLineEdit()
        self.address.setMinimumWidth(140)
        self.address.setMaximumWidth(140)
        self.layout.addWidget(self.address, 0, 1)

        self.startButton = QtGui.QPushButton()
        self.startButton.setText('Start log')
        self.layout.addWidget(self.startButton, 99, 0)
        self.startButton.setEnabled(False)

        self.stopButton = QtGui.QPushButton()
        self.stopButton.setText('Stop log')
        self.layout.addWidget(self.stopButton, 99, 1)
        self.stopButton.setEnabled(False)

        self.textDisplay = QtGui.QLabel()
        self.textDisplay.setText('>>')
        self.layout.addWidget(self.textDisplay, 99, 2)

        self.setComboInst()
        self.updateSignal()

    def setComboInst(self):
        for name, obj in inspect.getmembers(instruments):
            if inspect.ismodule(obj) and name.startswith('__') == False and name.startswith('abstract') == False:
                self.comboInst.addItem(name)

    def setSignalsSlots(self):
        self.comboInst.currentIndexChanged.connect(self.updateSignal)
        self.startButton.clicked.connect(self.startLog)
        self.stopButton.clicked.connect(self.stopLog)

    def runApp(self):
        self.w.show()
        sys.exit(self.a.exec_())

    @pyqtSlot()
    def updateSignal(self):
        for i in reversed(range(5, self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)

        defaultAddress = ''
        channelsAviables = []
        vtypesAviables = []

        exec('channelsAviables = instruments.%s.ALL_CHANNELS'%self.comboInst.currentText())
        exec('vtypesAviables = instruments.%s.ALL_VAL_TYPE'%self.comboInst.currentText())
        exec('defaultAddress = instruments.%s.ADDRESS'%self.comboInst.currentText())

        self.address.setText(defaultAddress)

        self.checkBoxChannels = [None]*len(channelsAviables)
        self.chListVtypes = [None]*len(self.checkBoxChannels)

        for i in range(len(self.checkBoxChannels)):
            self.checkBoxChannels[i] = QtGui.QCheckBox()
            self.checkBoxChannels[i].setText(channelsAviables[i])
            self.checkBoxChannels[i].setChecked(False)
            self.chListVtypes[i] = QtGui.QListWidget()
            for vtype in vtypesAviables:
                self.chListVtypes[i].addItem(vtype)
            self.chListVtypes[i].setCurrentRow(0)
            self.layout.addWidget(self.checkBoxChannels[i], i+3, 1)
            self.layout.addWidget(self.chListVtypes[i], i+3, 2)
            self.checkBoxChannels[i].stateChanged.connect(self.infoSignal)
            self.chListVtypes[i].currentItemChanged.connect(self.infoSignal)

        self.address.textChanged.connect(self.infoSignal)

        self.infoSignal()

    @pyqtSlot()
    def infoSignal(self):
        self.instToLog = self.comboInst.currentText()
        self.addressToLog = self.address.text()
        self.chToLog = []
        self.vTypeToLog = []

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

        self.textDisplay.setText('>> %s@%s - %s - %s'%(self.instToLog, self.addressToLog, self.chToLog, self.vTypeToLog))

        self.myLog = acq_routine(self.instToLog, self.chToLog, self.vTypeToLog, self.addressToLog)

    @pyqtSlot()
    def startLog(self):
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.address.setEnabled(False)
        self.comboInst.setEnabled(False)
        for i in self.checkBoxChannels:
            i.setEnabled(False)
        for i in self.chListVtypes:
            i.setEnabled(False)
        self.myLog.connect()
        self.myLog.start()

    @pyqtSlot()
    def stopLog(self):
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.address.setEnabled(True)
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
