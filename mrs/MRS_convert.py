# -*- coding: utf-8 -*-
"""
MRS_Convert.py

Version 1.4 
Modified 21/02/2020

Python3 version of the script. Converted from: Version 1.3.1

Created on 11 Dic 2019 @author: Patxi Torrealdea

...
Version 1.3.1
Modified 28/07/2017

Script to convert Philips MRS data to tarquin format for spectral processing
This script will deal with data acquired with multiple dynamic acquisitions
and saved in DICOM4 format.  Phasing and peak picking is done automatically but
can be adjusted manually

Created on Thu Oct 01 11:36:59 2015

@author: Alan Bainbridge

"""

# Import methods
import sys
import os
import numpy as np
from PyQt5 import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
try:
    import Spec_Module as sp
except:
    from mrs import Spec_Module as sp
import csv
from pathlib import Path

# Main function to run script is at the end of the file

# BASE_DIR = Path(__file__).resolve().parent.parent.parent
BASE_DIR = Path(__file__).parent

ICONS_DIR = BASE_DIR / "Icons"

HOME_DIR = Path.home()
dy = 25
# Define class for main GUI
class Maingui(QtGui.QMainWindow):
    # class Maingui(QtWidgets.QWidget):

    # --------Class Construction--------------------
    def __init__(self):
        super(Maingui, self).__init__()
        self.specoblist = []  # Hold list of spec objects
        self.curobject = 0  # Index of current object
        self.setsavedir = 0  # Flag.  Has save dir been set (1:Yes, 0:No)
        self.initUI()
        self.version = "1.4.1"
        self.resized.connect(self.resizeFunction)

    def initUI(self):
        
        
        
        # ---------Add menubar--------------------------------------------------
        menubar = self.menuBar()

        # Create menubar items ++++++++++++++++++++++
        # Items in 'File' menu

        # Get Directory Name
        OpenDirIcon = ICONS_DIR / "opened-folder.png"
        OpenDirIcon = str(OpenDirIcon.resolve())
        openDir = QtGui.QAction(QtGui.QIcon(OpenDirIcon), "Open Dir", self)
        openDir.setShortcut("Ctrl+D")
        openDir.triggered.connect(self.getdir)

        # Get Save Directory Name
        SaveDirIcon = ICONS_DIR / "save-48.png"
        SaveDirIcon = str(SaveDirIcon.resolve())
        saveDir = QtGui.QAction(QtGui.QIcon(SaveDirIcon), "Save Dir", self)
        saveDir.setShortcut("Ctrl+S")
        saveDir.triggered.connect(self.savedir)

        # Items in 'Tools' menu ++++++++++++++++++++++++
        # Convert individual file to JMRUI format
        tarqIcon = ICONS_DIR / "hat.ico"
        tarqIcon = str(tarqIcon.resolve())

        convfile = QtGui.QAction(
            QtGui.QIcon(tarqIcon), "Convert to JMRUI and Tarquin", self
        )
        convfile.triggered.connect(self.convert_to_all)

        # Convert individual file to Tarquin format
        convfileTarquin = QtGui.QAction(
            QtGui.QIcon(tarqIcon), "Convert processed to Tarquin", self
        )
        convfileTarquin.triggered.connect(self.Tarquin)

        convfileTarquinorig = QtGui.QAction(
            QtGui.QIcon(tarqIcon), "Convert original to Tarquin", self
        )
        convfileTarquinorig.triggered.connect(self.Tarquinorig)

        # Items in 'Phasing' menu +++++++++++++++++++++++++++
        phaseIcon = ICONS_DIR / "wave.png"
        phaseIcon = str(phaseIcon.resolve())
        phaseregion = QtGui.QAction(
            QtGui.QIcon(phaseIcon), "Phasing and Apodisation", self
        )
        phaseregion.triggered.connect(self.Phasereg)

        # about icon
        about_icon = ICONS_DIR / "about_icon.png"
        about_icon = str(about_icon.resolve())

        # Program Notes +++++++++++++++++++++++++++++++++++++++
        about = QtGui.QAction(QtGui.QIcon(about_icon), "About", self)
        about.triggered.connect(self.about)

        dcmmssg = QtGui.QAction(QtGui.QIcon(about_icon), "DICOM formats", self)
        dcmmssg.triggered.connect(self.dcmmssg)

        # Add the created items to menubar
        # Note - this part must come after item creation (above)
        fileMenu = menubar.addMenu("&File")
        fileMenu.addAction(openDir)
        fileMenu.addAction(saveDir)

        toolsMenu = menubar.addMenu("&Tools")
        toolsMenu.addAction(convfile)

        phasingMenu = menubar.addMenu("&Settings")
        phasingMenu.addAction(phaseregion)

        helpMenu = menubar.addMenu("&Notes")
        helpMenu.addAction(about)
        helpMenu.addAction(dcmmssg)


        self.self.scale = 1.6
        self.initial_width = int(1060*self.self.scale)
        self.initial_height = int(580*self.self.scale)
        self.wf = 1
        self.hf = 1
# ------Main Window Geometry-----------
        # This should come at the end once all GUI item are created
        self.setGeometry(300*self.self.scale, 300*self.self.scale, self.initial_width, self.initial_height)

        self.setWindowTitle("Tarquin Conversion Tool")
        self.setWindowIcon(QtGui.QIcon(tarqIcon))

        # self.setStyleSheet("QMainWindow {background: 'white';}");
        # self.setStyleSheet("color: blue;"
        #                 "background-color: white;"
        #                 "selection-color: blue;"
        #                 "selection-background-color: white;")




        # --------Add buttons---------------------------------------------------
        self.btnup = QtGui.QPushButton("Spec Up", self)
        self.btndown = QtGui.QPushButton("Spec Down", self)
        self.btnfup = QtGui.QPushButton("Next Frame", self)
        self.btnfdown = QtGui.QPushButton("Prev Frame", self)
        self.btninc = QtGui.QPushButton("Include Frame", self)
        self.btnexc = QtGui.QPushButton("Exclude Frame", self)
        self.btnorig = QtGui.QPushButton("Original", self)
        self.btnproc = QtGui.QPushButton("Processed", self)
        self.btnChoup = QtGui.QPushButton("Cho -", self)
        self.btnChodn = QtGui.QPushButton("Cho +", self)
        self.btnPhup = QtGui.QPushButton("Phase Inc", self)
        self.btnPhdn = QtGui.QPushButton("Phase Dec", self)
        self.btnCrup = QtGui.QPushButton("Cr -", self)
        self.btnCrdn = QtGui.QPushButton("Cr +", self)
        self.btnnophase = QtGui.QPushButton("Undo Phase", self)
        self.btnnoshift = QtGui.QPushButton("Undo Shift", self)
        self.btnfit = QtGui.QPushButton("Show Fit", self)


        self.btnreport  = QtGui.QPushButton(" 3) Compile MRS report ",self)
        self.btnreport.move(600*self.self.scale, (10+dy)*self.self.scale)
        self.btnreport.setStyleSheet("QPushButton {background-color: green; border-style: outset; border-width: 2px;border-radius: 10px;border-color: beige;font: bold ;min-width: 10em;padding: 6px;}")
        self.btnreport.adjustSize() 
        self.btnreport.resize(self.btnreport.sizeHint())
 
        self.btnreport.clicked.connect(self.convert_to_all)
        self.btnreport.hide()

        self.btnopen = QtGui.QPushButton("1)  Select folder with MRS data ", self)
        # Set button attributes
        # self.btnopen.resize(250, 30)
        self.btnopen.move(10*self.self.scale, (10+dy)*self.self.scale)
        self.btnopen.adjustSize()  

        self.btnopen.clicked.connect(self.btnopen_clicked)


        self.btnup.resize(self.btnup.sizeHint())
        self.btnup.move(20*self.scale, 530*self.scale)
        self.btnup.clicked.connect(self.specup)

        self.btndown.resize(self.btndown.sizeHint())
        self.btndown.move(20*self.scale, 550*self.scale)
        self.btndown.clicked.connect(self.specdown)

        
        self.btnfdown.resize(self.btnfdown.minimumSizeHint())
        self.btnfdown.move(533*self.scale, 550*self.scale)
        self.btnfdown.clicked.connect(self.framedown)

        self.btnfup.resize(self.btnfdown.size())
        self.btnfup.move(533*self.scale, 530*self.scale)
        self.btnfup.clicked.connect(self.frameup)


        self.btnexc.resize(self.btnexc.minimumSizeHint())
        self.btnexc.move(930*self.scale, 550*self.scale)
        self.btnexc.clicked.connect(self.ExcFrame)

        self.btninc.resize(self.btnexc.size())
        self.btninc.move(930*self.scale, 530*self.scale)
        self.btninc.clicked.connect(self.IncFrame)


        self.btnorig.resize(self.btnorig.minimumSizeHint())
        self.btnorig.move(120*self.scale, 530*self.scale)
        self.btnorig.clicked.connect(self.plotorigspec)

        self.btnnophase.resize(self.btnnophase.minimumSizeHint())
        self.btnnophase.move(280*self.scale, 550*self.scale)
        self.btnnophase.clicked.connect(self.undophase)

        self.btnnoshift.resize(self.btnnoshift.minimumSizeHint())
        self.btnnoshift.move(280*self.scale, 530*self.scale)
        self.btnnoshift.clicked.connect(self.undoshift)

        self.btnproc.resize(self.btnproc.minimumSizeHint())
        self.btnproc.move(120*self.scale, 550*self.scale)
        self.btnproc.clicked.connect(self.plotprocspec)

        self.btnChodn.resize(self.btnChodn.minimumSizeHint())
        self.btnChodn.move(745*self.scale, 550*self.scale)
        self.btnChodn.clicked.connect(self.Cho_dn)
        
        self.btnChoup.resize(self.btnChodn.size())
        self.btnChoup.move(745*self.scale, 530*self.scale)
        self.btnChoup.clicked.connect(self.Cho_up)

        
        self.btnPhdn.resize(self.btnPhdn.minimumSizeHint())
        self.btnPhdn.move(640*self.scale, 550*self.scale)
        self.btnPhdn.clicked.connect(self.Phase_dn)

        self.btnPhup.resize(self.btnPhdn.size())
        self.btnPhup.move(640*self.scale, 530*self.scale)
        self.btnPhup.clicked.connect(self.Phase_up)


        self.btnCrup.resize(self.btnCrup.minimumSizeHint())
        self.btnCrup.move(810*self.scale, 530*self.scale)
        self.btnCrup.clicked.connect(self.Cr_up)

        self.btnCrdn.resize(self.btnCrup.size())
        self.btnCrdn.move(810*self.scale, 550*self.scale)
        self.btnCrdn.clicked.connect(self.Cr_dn)

        self.btnfit.resize(self.btnfit.minimumSizeHint())
        self.btnfit.move(400*self.scale, 530*self.scale)
        self.btnfit.clicked.connect(self.plotfit)

        # -------Add text-------------------------------------------------------
        self.lbl = QtGui.QLabel(self)
        self.lbl.move(10*self.scale, (40+dy)*self.scale)
        self.lbl.setText("Open directory name:")
        self.lbl.adjustSize()

        self.lbl2 = QtGui.QLabel(self)
        self.lbl2.move(10*self.scale, (55+dy)*self.scale)
        self.lbl2.setText("Save directory name:")
        self.lbl2.adjustSize()

        self.lbl3 = QtGui.QLabel(self)
        self.lbl3.move(10*self.scale, (80+dy)*self.scale)
        self.lbl3.setText("Current Spectrum: ")
        self.lbl3.adjustSize()

        self.lbl4 = QtGui.QLabel(self)
        self.lbl4.move(300*self.scale, (80+dy)*self.scale)
        self.lbl4.setText("Number of MRS files found: 0")
        self.lbl4.adjustSize()

        self.lbl5 = QtGui.QLabel(self)
        self.lbl5.move(540*self.scale, (80+dy)*self.scale)
        self.lbl5.setText("Current Frame: ")
        self.lbl5.adjustSize()
        self.def_col = self.lbl5.palette().button().color();


        # ------- Add pyqtgraph objects ---------------------
        ## Switch to using white background and black foreground
        pg.setConfigOption("background", "w")
        pg.setConfigOption("foreground", "k")

        self.pw1 = pg.PlotWidget(self)
        self.pw1.setGeometry(QtCore.QRect(10*self.scale, (100+dy)*self.scale, int(500*self.width()*self.scale/self.initial_width), int(400*self.height()*self.scale/self.initial_height)))
        self.pw1.show()
        self.pw1.getViewBox().invertX(True)
        self.pw1.setXRange(0.4, 4.8, padding=0)
        self.pw1.setYRange(-0.2, 0.9, padding=0)

        self.p1 = self.pw1.plot(pen={"color": "b", "width": 2})
        self.p2 = self.pw1.plot(pen={"color": "r", "width": 2})
        self.p3 = self.pw1.plot(pen={"color": "r", "width": 2})

        self.pw2 = pg.PlotWidget(self)
        self.pw2.setGeometry(QtCore.QRect(540*self.scale, (100+dy)*self.scale, 500*self.scale, 400*self.scale))
        self.pw2.getViewBox().invertX(True)
        self.pw2.setXRange(0.4, 4.8, padding=0)
        self.pw2.setYRange(-0.02, 0.08, padding=0)

        self.pw2.show()
        self.p21 = self.pw2.plot(pen={"color": "b", "width": 2})
        self.p22 = self.pw2.plot(pen={"color": "r", "width": 2})
        self.p23 = self.pw2.plot(pen={"color": "g", "width": 2})

        # --------Add Message Box---------------
        # Note this opens a separate windpw with a message
        self.mssg = QtGui.QMessageBox()
        self.mssg.setGeometry(310*self.scale, 240*self.scale, 280*self.scale, 280*self.scale)
        self.mssg.setWindowTitle("About")
        self.mssg.setText(
            "Version 1.4.1 \n\n"
            + "Convert spectroscopy data to Tarquin and Jmrui format.\n\n"
            + "Please send any errors to balangb@gmail.com or papomail@gmail.com"
        )

        self.dcmfmt = QtGui.QMessageBox()
        self.dcmfmt.setGeometry(310*self.scale, 240*self.scale, 280*self.scale, 280*self.scale)
        self.dcmfmt.setWindowTitle("DICOM formats")
        self.dcmfmt.setText("Only Dicom4 data can be processed\n\n")

        
        
        
        self.show()

        # ## Handle view resizing
        # def updateViews():
        #     ## view has resized; update auxiliary views to match
        #     self.pw2.setGeometry(self.pw1.sceneBoundingRect())
        #     self.pw1.linkedViewChanged(self.pw1, self.pw2.XAxis)

        # updateViews()
        # self.pw1.vb.sigResized.connect(updateViews)

    # --------Class Methods-----------------------------------

    
    resized = QtCore.pyqtSignal()
    # def  __init__(self, parent=None):
    #     super(Window, self).__init__(parent=parent)
    #     ui = Ui_MainWindow()
    #     ui.setupUi(self)
    #     self.resized.connect(self.someFunction)

    def resizeEvent(self, event):
        self.resized.emit()
        return super(Maingui, self).resizeEvent(event)

    def resizeFunction(self):
        w = self.width()
        h = self.height()
        self.wf = w/self.initial_width
        self.hf = h/self.initial_height

#        print(f'App size {w}x{h} px')

        self.btnreport.move(int(600*self.wf*self.scale), int((10+dy)*self.hf*self.scale))

        if "2) " in self.btnopen.text():
             self.btnopen.move(int(200*self.wf), int((10+dy)*self.hf*self.scale))
   
        self.btnup.move(int(20*self.wf*self.scale), int(530*self.hf*self.scale))
        
        self.btndown.move(int(20*self.wf*self.scale), int(550*self.hf*self.scale))
        
        self.btnfup.move(int(533*self.wf*self.scale), int(530*self.hf*self.scale))
        
        self.btnfdown.move(int(533*self.wf*self.scale), int(550*self.hf*self.scale))
        
        self.btninc.move(int(930*self.wf*self.scale), int(530*self.hf*self.scale))
        
        self.btnexc.move(int(930*self.wf*self.scale), int(550*self.hf*self.scale))
        
        self.btnorig.move(int(120*self.wf*self.scale), int(530*self.hf*self.scale))
        
        self.btnnophase.move(int(280*self.wf*self.scale), int(self.hf*550*self.scale))
        
        self.btnnoshift.move(int(280*self.wf*self.scale), int(self.hf*530*self.scale))
        
        self.btnproc.move(int(120*self.wf*self.scale), int(self.hf*550*self.scale))
        
        self.btnChoup.move(int(745*self.wf*self.scale), int(self.hf*530*self.scale))
       
        self.btnChodn.move(int(745*self.wf*self.scale), int(self.hf*550*self.scale))
        
        self.btnPhup.move(int(640*self.wf*self.scale), int(self.hf*530*self.scale))
        
        self.btnPhdn.move(int(640*self.wf*self.scale), int(self.hf*550*self.scale))
        
        self.btnCrup.move(int(810*self.wf*self.scale), int(self.hf*530*self.scale))
        
        self.btnCrdn.move(int(810*self.wf*self.scale), int(self.hf*550*self.scale))
        
        self.btnfit.move(int(400*self.wf*self.scale), int(self.hf*530*self.scale))
        
        self.lbl.move(int(10*self.wf*self.scale), int(self.hf*(40+dy)*self.scale))
        
        self.lbl2.move(int(10*self.wf*self.scale), int(self.hf*(55+dy)*self.scale))
        
        self.lbl3.move(int(10*self.wf*self.scale), int(self.hf*(80+dy)*self.scale))
        
        self.lbl4.move(int(300*self.wf*self.scale), int(self.hf*(80+dy)*self.scale))
        
        self.lbl5.move(int(540*self.wf*self.scale), int(self.hf*(80+dy)*self.scale))

        self.pw1.move(int(10*self.wf*self.scale), int((100+dy)*self.hf*self.scale))
        self.pw1.resize(int(500*self.wf*self.scale), int((400)*self.hf*self.scale))

        self.pw2.move(int(540*self.wf*self.scale), int((100+dy)*self.hf*self.scale))
        self.pw2.resize(int(500*self.wf*self.scale), int((400)*self.hf*self.scale))


    def btnopen_clicked(self):
        
        if "1) " in self.btnopen.text():
            
            self.getdir()
            framenum = self.specoblist[self.curobject].curframe + 1
            totalframes = int(self.specoblist[self.curobject].Frames / 2)  
            self.btnopen.setText(f"2) Check and adjust spectra if needed: {str(framenum)}/{str(totalframes)}")
            self.btnopen.setStyleSheet("QPushButton {color: #f2c885;}")
            self.btnopen.move(int(200*self.wf), int((10+dy)*self.hf))
            self.btnopen.adjustSize()

        elif "2) " in self.btnopen.text():
            self.frameup()
            


    def check_btnopen(self):
        
        if "2) " in self.btnopen.text():
            self.btnopen.move(int(200*self.wf*self.scale), int((10+dy)*self.hf*self.scale))
            framenum = self.specoblist[self.curobject].curframe + 1
            totalframes = int(self.specoblist[self.curobject].Frames / 2)    
            self.btnopen.setText(f"2) Check and adjust spectra if needed: {str(framenum)}/{str(totalframes)}")
            self.btnopen.setStyleSheet("QPushButton {color: #f2c885;}") 

        if int(self.specoblist[self.curobject].curframe + 1) == int(self.specoblist[self.curobject].Frames / 2):
                self.btnreport.show()





    def about(self):
        """Message box to display script information
        """
        self.mssg.show()

    def dcmmssg(self):
        """Message box to display info about how DICOM formats are treated
        """
        self.dcmfmt.show()

    def getdir(self):
        """Array to hold list of SpecObject objects - initialised empty
        """
        self.specoblist = []
        """self.curobject is index of current object in self.specoblist list        
        """
        self.curobject = 0

        # Standard Open Directory Dialog box
        self.dirname = str(
            QtGui.QFileDialog.getExistingDirectory(
                self, "Open Directory", str(HOME_DIR.resolve())
            )
        )

        # Display name of 'open' directory in main window (self.lb1)
        textout = "Open directory name: " + self.dirname
        self.lbl.setText(textout)
        self.lbl.adjustSize()

        # dirpass string passed when initialising SpecObject object
        # Used for naming files that are written later
        dirpass = self.dirname.replace(":", "").replace("\\", "_")
        # use os.chdir to get into chosen directory
        os.chdir(self.dirname)

        # get list of files in chosen directory
        filelist = os.listdir(self.dirname)

        # loop through files in dir and determine which ones are enhanced dicoms
        for curfile in filelist:

            # If curfile is a directory
            if os.path.isdir(curfile):
                # change to daughter directory
                # curdir = self.dirname + '\\' + curfile
                curdir = str(Path(self.dirname, curfile).resolve())

                os.chdir(curdir)
                # Get filelist in daughter directory
                filelist2 = os.listdir(curdir)
                # Loop through files in daughter directory
                for curfile2 in filelist2:
                    # Create object of type SpecObject
                    temp_spec_object = sp.SpecObject(curfile2, dirpass)
                    # If temp_spec_object is from a DICOM 4 MRS file
                    if temp_spec_object.isspec != 0:
                        # Append to self.specoblist
                        self.specoblist.append(temp_spec_object)
                        # Call function to plot original spectrum in window
                        self.plotorigspec()
            # Make sure we are in parent directory
            os.chdir(self.dirname)
            # Create object of type SpecObject

            temp_spec_object = sp.SpecObject(curfile, dirpass)
            # If temp_spec_object is from a DICOM 4 MRS file
            if temp_spec_object.isspec != 0:
                # Append to self.specoblist
                self.specoblist.append(temp_spec_object)
                # Call function to plot original spectrum in window
                self.plotorigspec()
                self.plotframe()

                print(self.specoblist)  # Patcheck

        # Display message in main window (self.lb4): number of MRS files found
        textout = "Number of MRS files found: " + str(np.size(self.specoblist))
        self.lbl4.setText(textout)
        self.lbl4.adjustSize()

    # Plot original, unprocessed spectrum in main window
    def plotorigspec(self):
        self.p1.clear()
        self.p2.clear()
        self.p3.clear()
        # set data for pen p1 as original summed spectrum with no processing
        self.p1.setData(y=np.real(self.specoblist[self.curobject].OriginalSpectrum), x=self.specoblist[self.curobject].fake_ppms )
        

        # Markers will show bounds of phasing area
        x1_marker = np.ones(2)
        x2_marker = np.ones(2)
        y_marker = np.ones(2)
        # get min and max of spectrum for y marker
        y_marker[0] = min(np.real(self.specoblist[self.curobject].OriginalSpectrum))
        y_marker[1] = max(np.real(self.specoblist[self.curobject].OriginalSpectrum))
        # Get phase limits for x marker
        x1_marker[0] = self.specoblist[self.curobject].plim_l*(-0.01529464093)+20.33273
        x1_marker[1] = x1_marker[0]
        x2_marker[0] = self.specoblist[self.curobject].plim_r*(-0.01529464093)+20.33273
        x2_marker[1] = x2_marker[0]
        # Set pens p2 and p3 as the phase area limits
        self.p2.setData(x1_marker, y_marker)
        self.p3.setData(x2_marker, y_marker)
        self.PlotType = 1
        textout = "Original Spectrum: " + self.specoblist[self.curobject].filename
        self.lbl3.setText(textout)
        self.lbl3.adjustSize()

    # Plot processed spectrum in main window
    def plotprocspec(self):
        self.p1.clear()
        self.p2.clear()
        self.p3.clear()
        # set data for pen p1 as processed summed spectrum with no processing
        self.p1.setData(y=np.real(self.specoblist[self.curobject].FinalSpectrumauto), x=self.specoblist[self.curobject].fake_ppms)
        # self.p1.getViewBox().invertX(True)

        # Markers will show bounds of phasing area
        x1_marker = np.ones(2)
        x2_marker = np.ones(2)
        y_marker = np.ones(2)
        # get min and max of spectrum for y marker
        y_marker[0] = min(np.real(self.specoblist[self.curobject].FinalSpectrumauto))
        y_marker[1] = max(np.real(self.specoblist[self.curobject].FinalSpectrumauto))
        # Get phase limits for x marker
        x1_marker[0] = self.specoblist[self.curobject].plim_l*(-0.01529464093)+20.33273
        x1_marker[1] = x1_marker[0]
        x2_marker[0] = self.specoblist[self.curobject].plim_r*(-0.01529464093)+20.33273
        x2_marker[1] = x2_marker[0]
        self.p2.setData(x1_marker, y_marker)
        self.p3.setData(x2_marker, y_marker)
        self.PlotType = 1
        textout = "Processed Spectrum: " + self.specoblist[self.curobject].filename
        self.lbl3.setText(textout)
        self.lbl3.adjustSize()

    def Phasereg(self):
        leftinit = self.specoblist[self.curobject].plim_l
        rightinit = self.specoblist[self.curobject].plim_r
        apodinit = self.specoblist[self.curobject].apod_const
        dialog = PhaseDialog(leftinit, rightinit, apodinit)
        if dialog.exec_():
            leftlim = dialog.leftlim.text()
            rightlim = dialog.rightlim.text()
            apod_const = dialog.apod_const.text()

        try:
            left_int = int(leftlim)
        except:
            left_int = leftinit

        try:
            right_int = int(rightlim)
        except:
            right_int = rightinit

        try:
            apod_int = float(apod_const)
        except:
            apod_int = apodinit

        self.specoblist[self.curobject].plim_l = left_int
        self.specoblist[self.curobject].plim_r = right_int
        self.specoblist[self.curobject].apod_const = apod_int

        self.specoblist[self.curobject].autophase()
        self.plotprocspec()

    def savedir(self):
        proposed_savedir = Path(self.dirname).parent
        proposed_savedir = proposed_savedir / "resultsMRS"
        if proposed_savedir.exists():
            self.savedirname = QtGui.QFileDialog.getExistingDirectory(
                    self,
                    'Save Directory (WARNING: saving in "resultMRS" will overwrite previous results)',
                    str(Path(self.dirname).parent.resolve()),)
        
        else:
            proposed_savedir.mkdir(parents=True, exist_ok=True)
            self.savedirname = QtGui.QFileDialog.getExistingDirectory(self,
                    'Save Directory (default: "resultMRS" inside patient folder)',
                    str(proposed_savedir.resolve()),)

            if self.savedirname != str(proposed_savedir.resolve()):
                proposed_savedir.rmdir()

        textout = "Save directory name: " + self.savedirname
        self.lbl2.setText(textout)
        self.lbl2.adjustSize()
        self.setsavedir = 1

    def specup(self):
        self.curobject += 1
        try:
            self.plotorigspec()
        except:
            self.curobject -= 1

    def specdown(self):
        if self.curobject > 0:
            self.curobject -= 1
            self.plotorigspec()

    def Tarquin(self):
        if self.setsavedir == 0:
            self.savedir()
        self.specoblist[self.curobject].writeTarquin(self.savedirname)

    def convert_to_all(self):
        if self.setsavedir == 0:
            self.savedir()

        self.specoblist[self.curobject].writeTarquin(self.savedirname)
        self.specoblist[self.curobject].writelogfile(self.savedirname, self.version)
        self.specoblist[self.curobject].fitTarquin(self.savedirname)
        # self.plotfit()

        self.lbl2.setText(self.specoblist[self.curobject].report_completed_msg)
        self.lbl2.adjustSize()
        self.lbl2.setStyleSheet("QLabel {color: green;}")

    def Tarquinorig(self):
        if self.setsavedir == 0:
            self.savedir()
        self.specoblist[self.curobject].writeTarquinorig(self.savedirname)

    def frameup(self):
        self.specoblist[self.curobject].frameup()
        self.check_btnopen()
        self.plotframe()


    def framedown(self):
        self.specoblist[self.curobject].framedown()
        self.check_btnopen()
        self.plotframe()


    def plotframe(self):
        self.p21.setData(y=np.real(self.specoblist[self.curobject].current_frame), x=self.specoblist[self.curobject].fake_ppms)
        # self.p21.getViewBox().invertX(True)
        cur_frame = self.specoblist[self.curobject].curframe

        x1_marker = np.ones(2)
        x2_marker = np.ones(2)
        y_marker = np.ones(2)
        y_marker[0] = min(np.real(self.specoblist[self.curobject].current_frame))
        y_marker[1] = max(np.real(self.specoblist[self.curobject].current_frame))
        x1_marker[0] = self.specoblist[self.curobject].peakposarr[cur_frame][0]*(-0.01529464093)+20.33273
        x1_marker[1] = x1_marker[0]
        x2_marker[0] = self.specoblist[self.curobject].peakposarr[cur_frame][1]*(-0.01529464093)+20.33273
        x2_marker[1] = x2_marker[0]
        self.p22.setData(x1_marker, y_marker)
        # self.p22.getViewBox().invertX(True)
        self.p23.setData(x2_marker, y_marker)
        # self.p23.getViewBox().invertX(True)

        if cur_frame + 1 == 1:
            ordinal_sufix = "st"

        elif cur_frame + 1 == 2:
            ordinal_sufix = "nd"

        elif cur_frame + 1 == 3:
            ordinal_sufix = "rd"

        else:
            ordinal_sufix = "th"

        if self.specoblist[self.curobject].IncludeFrame[cur_frame] == 1:
            textout = f'Include Frame: {(cur_frame + 1)}{ordinal_sufix} : {self.specoblist[self.curobject].PatName}'
            
        else:
            textout = f'Exclude Frame: {(cur_frame + 1)}{ordinal_sufix} : {self.specoblist[self.curobject].PatName}'

            
        self.lbl5.setText(textout)
        self.lbl5.adjustSize()
        if 'Exclude' in textout:
            self.lbl5.setStyleSheet("QLabel {color: red;}")
        else:
            self.lbl5.setStyleSheet("QLabel {color: self.def_col;}")

    def undophase(self):
        self.specoblist[self.curobject].undophase()
        self.plotframe()
        self.plotprocspec()

    def undoshift(self):
        self.specoblist[self.curobject].undoshift()
        self.plotframe()
        self.plotprocspec()

    def IncFrame(self):
        cur_frame = self.specoblist[self.curobject].curframe
        self.specoblist[self.curobject].IncludeFrame[cur_frame] = 1

        # textout = f'Include Frame: {(cur_frame + 1)} : {self.specoblist[self.curobject].PatName}'

        # self.lbl5.setText(textout)
        # self.lbl5.adjustSize()

        self.specoblist[self.curobject].addframes()
        self.plotframe()
        self.plotprocspec()

    def ExcFrame(self):
        cur_frame = self.specoblist[self.curobject].curframe
        self.specoblist[self.curobject].IncludeFrame[cur_frame] = 0
        # textout = f'Exclude Frame: {(cur_frame + 1)} : {self.specoblist[self.curobject].PatName}'

        # self.lbl5.setText(textout)
        # self.lbl5.adjustSize()
        


        self.specoblist[self.curobject].addframes()
        self.plotframe()
        self.plotprocspec()

    def Phase_up(self):
        increment = 5
        self.specoblist[self.curobject].phaseinc(increment)
        self.plotframe()
        self.plotprocspec()

    def Phase_dn(self):
        increment = -5
        self.specoblist[self.curobject].phaseinc(increment)
        self.plotframe()
        self.plotprocspec()

    def Cho_up(self):
        increment = 1
        self.specoblist[self.curobject].Choinc(increment)
        self.plotframe()
        self.plotprocspec()

    def Cho_dn(self):
        increment = -1
        self.specoblist[self.curobject].Choinc(increment)
        self.plotframe()
        self.plotprocspec()

    def Cr_up(self):
        increment = 1
        self.specoblist[self.curobject].Crinc(increment)
        self.plotframe()
        self.plotprocspec()

    def Cr_dn(self):
        increment = -1
        self.specoblist[self.curobject].Crinc(increment)
        self.plotframe()
        self.plotprocspec()

    def plotfit(self):
        try:
            fit_file = self.specoblist[self.curobject].fitout
            PPM = []
            Data = []
            Fit = []

            with open(fit_file) as csvfile:
                lineread = csv.reader(csvfile)
                counter = 0
                for row in lineread:
                    if counter > 1:
                        PPM.append(float(row[0]))
                        Data.append(float(row[1]))
                        Fit.append(float(row[2]))
                    counter = counter + 1

            Data_arr = np.array(Data, float)
            Fit_arr = np.array(Fit, float)
            PPM_arr = np.array(PPM, float)

            self.p1.clear()
            self.p2.clear()        
            self.p3.clear()

            self.p1.setData(y=Data_arr, x=PPM_arr)
            self.p2.setData(y=Fit_arr, x=PPM_arr)
            self.pw1.setXRange(0.4, 4.8, padding=0)
            self.pw1.setYRange(-0.02, 0.08, padding=0)

        except:
            dummy = 1


class PhaseDialog(QtWidgets.QDialog):
    # SLOT = QtCore.pyqtSignal(str)

    def __init__(self, leftinit, rightinit, apod_const, parent=None):
        super(PhaseDialog, self).__init__(parent)
        self.left_string = str(leftinit)
        self.right_string = str(rightinit)
        self.apod_string = str(apod_const)

        rightlabel = QtGui.QLabel("&Right Limit:")
        self.rightlim = QtGui.QLineEdit(self.right_string)
        rightlabel.setBuddy(self.rightlim)

        leftlabel = QtGui.QLabel("&Left Limit:")
        self.leftlim = QtGui.QLineEdit(self.left_string)
        leftlabel.setBuddy(self.leftlim)

        apodlabel = QtGui.QLabel("&Apodisation:")
        self.apod_const = QtGui.QLineEdit(self.apod_string)
        apodlabel.setBuddy(self.apod_const)

        self.buttonbox = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok
        )
        # buttonbox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)

        grid = QtGui.QGridLayout()
        grid.addWidget(leftlabel, 0, 0)
        grid.addWidget(self.leftlim, 0, 1)
        grid.addWidget(rightlabel, 1, 0)
        grid.addWidget(self.rightlim, 1, 1)
        grid.addWidget(apodlabel, 2, 0)
        grid.addWidget(self.apod_const, 2, 1)
        grid.addWidget(self.buttonbox, 4, 0, 3, 2)
        self.setLayout(grid)

        self.buttonbox.accepted.connect(self.accept)
        self.buttonbox.rejected.connect(self.reject)

        self.setWindowTitle("Enter Limits")


# Main function - needed to run script
def main():

    app = QtGui.QApplication(sys.argv)
    ex = Maingui()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
