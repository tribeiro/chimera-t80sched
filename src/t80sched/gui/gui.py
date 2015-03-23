
import sys,os

from PyQt4 import QtCore,QtGui,uic
import logging

#from astropy.io import fits as pyfits
import numpy as np

#from vtmodel import *

################################################################################
#
#

class SchedulerGUI(QtGui.QMainWindow):


    ############################################################################
    #
    #

    def __init__(self):

        super(SchedulerGUI, self).__init__()

        self.uipath = os.path.join(os.path.dirname(__file__),
                                   'main.ui')


    #
    #
    ############################################################################

    ############################################################################
    #
    #

    def initGUI(self):

        self.ui = uic.loadUi(self.uipath,self)

        self.ui.hour.axes.plot([0,1,2],[0,1,0],'o-')
        self.ui.hour.draw()
        self.ui.hour.axes.hold(False)

        someDT = QtCore.QDateTime(2015,01,01,12,00,00)
        self.ui.dateTimeEditStart.setDateTime(someDT)

        self.ui.dateTimeEditEnd.setDateTime(someDT)


    #
    #
    ############################################################################


    #
    #
    ################################################################################

