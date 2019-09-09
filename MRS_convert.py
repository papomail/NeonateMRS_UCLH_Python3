# -*- coding: utf-8 -*-
"""
'Last Modified by Patxi on August 2019.' \


MRS_Convert.py

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
import os as os
import numpy as np
#import dicom as dcm
from PyQt5 import QtGui
from PyQt5 import QtCore
import pyqtgraph as pg
import Spec_Module as sp
import csv as csv 
from pathlib import Path


#Main function to run script is at the end of the file

#BASE_DIR = Path(__file__).resolve().parent.parent.parent
BASE_DIR = Path(__file__).parent.parent.parent

ICONS_DIR= BASE_DIR / 'Icons' 

HOME_DIR = Path.home()

#Define class for main GUI
class Maingui(QtGui.QMainWindow):
    #--------Class Construction--------------------
    def __init__(self):
        super(Maingui, self).__init__()
        self.specoblist = []        #Hold list of spec objects
        self.curobject = 0          #Index of current object
        self.setsavedir = 0         #Flag.  Has save dir been set (1:Yes, 0:No)
        self.initUI()
        self.version = '1.3.1'               

        
    def initUI(self):  
        #---------Add menubar-------------------------------------------------- 
        menubar = self.menuBar()
        
        #Create menubar items ++++++++++++++++++++++
        #Items in 'File' menu

        #Get Directory Name
        OpenDirIcon=ICONS_DIR / 'opened-folder.png'
        OpenDirIcon=str(OpenDirIcon.resolve())
        openDir = QtGui.QAction(QtGui.QIcon(OpenDirIcon),
                                'Open Dir', self)
        openDir.setShortcut('Ctrl+D')
        openDir.triggered.connect(self.getdir)
        
        #Get Save Directory Name
        SaveDirIcon=ICONS_DIR / 'save-48.png'
        SaveDirIcon=str(SaveDirIcon.resolve())
        saveDir = QtGui.QAction(QtGui.QIcon(SaveDirIcon),
                                'Save Dir', self)
        saveDir.setShortcut('Ctrl+S')
        saveDir.triggered.connect(self.savedir)        
        
        #Items in 'Tools' menu ++++++++++++++++++++++++
        #Convert individual file to JMRUI format     
        tarqIcon=ICONS_DIR / 'hat.ico'
        tarqIcon=str(tarqIcon.resolve())

        convfile = QtGui.QAction(QtGui.QIcon(tarqIcon),
                                    'Convert processed to JMRUI', self)
        convfile.triggered.connect(self.jmrui)

        convfile = QtGui.QAction(QtGui.QIcon(tarqIcon),
                                    'Convert to JMRUI and Tarquin', self)
        convfile.triggered.connect(self.convert_to_all)


        #Convert individual file to Tarquin format         
        convfileTarquin = QtGui.QAction(QtGui.QIcon(tarqIcon),
                                    'Convert processed to Tarquin', self)
        convfileTarquin.triggered.connect(self.Tarquin)

        convfileTarquinorig = QtGui.QAction(QtGui.QIcon(tarqIcon),
                                    'Convert original to Tarquin', self)
        convfileTarquinorig.triggered.connect(self.Tarquinorig)         
        
        
        #Items in 'Phasing' menu +++++++++++++++++++++++++++
        phaseIcon=ICONS_DIR / 'wave.png'
        phaseIcon=str(phaseIcon.resolve())
        phaseregion = QtGui.QAction(QtGui.QIcon(phaseIcon),
                                    'Phasing and Adopisation', self)
        phaseregion.triggered.connect(self.Phasereg)                            
       
       
       
        #Program Notes +++++++++++++++++++++++++++++++++++++++
        about = QtGui.QAction(QtGui.QIcon('C:\\icons\\menu\\about.png'),
                                'About', self)
        about.triggered.connect(self.about)  
        
        dcmmssg = QtGui.QAction(QtGui.QIcon('C:\\icons\\menu\\about.png'),
                                'DICOM formats', self)
        dcmmssg.triggered.connect(self.dcmmssg) 
        
        
        #Add the created items to menubar
        #Note - this part must come after item creation (above)
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openDir)
        fileMenu.addAction(saveDir)
        
        toolsMenu = menubar.addMenu('&Tools')
        toolsMenu.addAction(convfile)


        phasingMenu = menubar.addMenu('&Settings')
        phasingMenu.addAction(phaseregion)
        
        helpMenu = menubar.addMenu('&Notes')
        helpMenu.addAction(about)
        helpMenu.addAction(dcmmssg)
 


       
        #--------Add buttons---------------------------------------------------
        btnup = QtGui.QPushButton('Spec up', self)  
        btndown = QtGui.QPushButton('Spec Down', self)
        btnfup = QtGui.QPushButton('F_up', self)
        btnfdown = QtGui.QPushButton('F_down', self)      
        btninc = QtGui.QPushButton('Include', self)
        btnexc = QtGui.QPushButton('Exclude', self)
        btnorig = QtGui.QPushButton('Original', self)
        btnproc = QtGui.QPushButton('Processed', self)
        btnChoup = QtGui.QPushButton('Peak1 +', self)
        btnChodn = QtGui.QPushButton('Peak1 -', self)
        btnPhup = QtGui.QPushButton('Phase +', self)
        btnPhdn = QtGui.QPushButton('Phase -', self)
        btnCrup = QtGui.QPushButton('Peak2 +', self)
        btnCrdn = QtGui.QPushButton('Peak2 -', self)
        btnnophase = QtGui.QPushButton('undo phase', self)
        btnnoshift = QtGui.QPushButton('undo shift', self) 
        btnfit = QtGui.QPushButton('Show Fit', self)
        
        #Set button attributes
        btnup.resize(btnup.sizeHint())
        btnup.move(20,510)  
        btnup.clicked.connect(self.specup)
        
        btndown.resize(btndown.sizeHint())
        btndown.move(20,540)  
        btndown.clicked.connect(self.specdown)
        
       
        btnfup.resize(btnfup.sizeHint())
        btnfup.move(560,510)  
        btnfup.clicked.connect(self.frameup)
        
        btnfdown.resize(btndown.sizeHint())
        btnfdown.move(560,540)  
        btnfdown.clicked.connect(self.framedown)
        
        btninc.resize(btninc.sizeHint())
        btninc.move(940,510)  
        btninc.clicked.connect(self.IncFrame)
        
        btnexc.resize(btnexc.sizeHint())
        btnexc.move(940,540)  
        btnexc.clicked.connect(self.ExcFrame)
        
        btnorig.resize(btnorig.sizeHint())
        btnorig.move(120,510)  
        btnorig.clicked.connect(self.plotorigspec)
        
        btnnophase.resize(btnnophase.sizeHint())
        btnnophase.move(300,510)  
        btnnophase.clicked.connect(self.undophase)
        
        btnnoshift.resize(btnnoshift.sizeHint())
        btnnoshift.move(300,540)  
        btnnoshift.clicked.connect(self.undoshift)
        
        btnproc.resize(btnproc.sizeHint())
        btnproc.move(120,540)  
        btnproc.clicked.connect(self.plotprocspec)
        
        btnChoup.resize(btnChoup.sizeHint())
        btnChoup.move(720,510)  
        btnChoup.clicked.connect(self.Cho_up)

        btnChodn.resize(btnChodn.sizeHint())
        btnChodn.move(720,540)  
        btnChodn.clicked.connect(self.Cho_dn) 

        btnPhup.resize(btnPhup.sizeHint())
        btnPhup.move(640,510)  
        btnPhup.clicked.connect(self.Phase_up)

        btnPhdn.resize(btnPhdn.sizeHint())
        btnPhdn.move(640,540)  
        btnPhdn.clicked.connect(self.Phase_dn)   

        btnCrup.resize(btnCrup.sizeHint())
        btnCrup.move(800,510)  
        btnCrup.clicked.connect(self.Cr_up)

        btnCrdn.resize(btnCrdn.sizeHint())
        btnCrdn.move(800,540)  
        btnCrdn.clicked.connect(self.Cr_dn)
        
        btnfit.resize(btnfit.sizeHint())
        btnfit.move(400,510)  
        btnfit.clicked.connect(self.plotfit)
           
        #-------Add text-------------------------------------------------------
        self.lbl = QtGui.QLabel(self)
        self.lbl.move(10,30)
        self.lbl.setText('Open directory name:')
        self.lbl.adjustSize()     
        
        self.lbl2 = QtGui.QLabel(self)
        self.lbl2.move(10,50)
        self.lbl2.setText('Save directory name:')
        self.lbl2.adjustSize() 
        
        self.lbl3 = QtGui.QLabel(self)
        self.lbl3.move(10,80)
        self.lbl3.setText('Current Spectrum: ')
        self.lbl3.adjustSize() 
        
        self.lbl4 = QtGui.QLabel(self)
        self.lbl4.move(300,80)
        self.lbl4.setText('Number of MRS files found: 0')
        self.lbl4.adjustSize()
        
        self.lbl5 = QtGui.QLabel(self)
        self.lbl5.move(540,80)
        self.lbl5.setText('Current Frame: ')
        self.lbl5.adjustSize()


        
        #------- Add pyqtgraph objects ---------------------
        ## Switch to using white background and black foreground
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        self.plotwidget = pg.PlotWidget(self)
        self.plotwidget.setGeometry(QtCore.QRect(10, 100, 500, 400))
        self.plotwidget.show()
        self.p1 = self.plotwidget.plot(pen = {'color': 'b', 'width': 1})
        self.p2 = self.plotwidget.plot(pen = {'color': 'r', 'width': 1})
        self.p3 = self.plotwidget.plot(pen = {'color': 'r', 'width': 1})

        self.plotwidget2 = pg.PlotWidget(self)
        self.plotwidget2.setGeometry(QtCore.QRect(540, 100, 500, 400))
        self.plotwidget2.show()
        self.p21 = self.plotwidget2.plot(pen = {'color': 'b', 'width': 1})
        self.p22 = self.plotwidget2.plot(pen = {'color': 'r', 'width': 1})
        self.p23 = self.plotwidget2.plot(pen = {'color': 'g', 'width': 1})
        
        
        #--------Add Message Box---------------
        #Note this opens a separate windpw with a message
        self.mssg = QtGui.QMessageBox()
        self.mssg.setGeometry(310, 240, 280,280)
        self.mssg.setWindowTitle('About')
        self.mssg.setText('Version 1.3.1 \n\n' \
                + 'Convert spectroscopy data to Tarquin and Jmrui format.\n\n' \
                + 'Please send any errors to balangb@gmail.com')
                
        self.dcmfmt = QtGui.QMessageBox()
        self.dcmfmt.setGeometry(310, 240, 280,280)
        self.dcmfmt.setWindowTitle('DICOM formats')
        self.dcmfmt.setText('Only Dicom4 data can be processed\n\n')
        
        #------Main Window Geometry-----------
        #This should come at the end once all GUI item are created
        self.setGeometry(300, 300, 1060, 580)
        self.setWindowTitle('Tarquin Conversion Tool')
        self.setWindowIcon(QtGui.QIcon('C:\\icons\\menu\\advanced.png'))
        self.show()
        
        
    #--------Class Methods-----------------------------------  
    def about(self):
        #Message box to display script information
        self.mssg.show()
        
    def dcmmssg(self):
        #Message box to display info about how DICOM formats are treated
        self.dcmfmt.show()
        
    def getdir(self):
        #Array to hold list of SpecObject objects - initialised empty
        self.specoblist = []

        #self.curobject is index of current object in self.specoblist list        
        self.curobject = 0
        
        #Standard Open Directory Dialog box
        self.dirname = str(QtGui.QFileDialog.getExistingDirectory(self,
                'Open Directory',  str(HOME_DIR.resolve())  ))
        
        #Display name of 'open' directory in main window (self.lb1)                      
        textout = 'Open directory name: ' + self.dirname
        self.lbl.setText(textout)
        self.lbl.adjustSize()
        
        #dirpass string passed when initialising SpecObject object
        #Used for naming files that are written later
        dirpass = self.dirname.replace(':', '').replace('\\', '_')
        # use os.chdir to get into chosen directory
        os.chdir(self.dirname)
        
        #get list of files in chosen directory
        filelist = os.listdir(self.dirname)
 
          
        # loop through files in dir and determine which ones are enhanced dicoms
        for curfile in filelist:

            #If curfile is a directory
            if os.path.isdir(curfile):
                #change to daughter directory
                #curdir = self.dirname + '\\' + curfile
                curdir = str(Path(self.dirname , curfile).resolve())

                os.chdir(curdir)
                #Get filelist in daughter directory
                filelist2 = os.listdir(curdir)
                #Loop through files in daughter directory
                for curfile2 in filelist2:
                    #Create object of type SpecObject
                    temp_spec_object = sp.SpecObject(curfile2, dirpass)
                    #If temp_spec_object is from a DICOM 4 MRS file
                    if temp_spec_object.isspec != 0:
                        #Append to self.specoblist
                        self.specoblist.append(temp_spec_object)
                        #Call function to plot original spectrum in window
                        self.plotorigspec()
            #Make sure we are in parent directory
            os.chdir(self.dirname)
            #Create object of type SpecObject
            


            temp_spec_object = sp.SpecObject(curfile, dirpass)
            #If temp_spec_object is from a DICOM 4 MRS file
            if temp_spec_object.isspec != 0:
                #Append to self.specoblist
                self.specoblist.append(temp_spec_object)
                #Call function to plot original spectrum in window
                self.plotorigspec()
                self.plotframe()
                
        #Display message in main window (self.lb4): number of MRS files found      
        textout = 'Number of MRS files found: ' + str(np.size(self.specoblist))
        self.lbl4.setText(textout)
        self.lbl4.adjustSize()



    #Plot original, unprocessed spectrum in main window
    def plotorigspec(self):
        self.p1.clear()
        self.p2.clear()
        self.p3.clear()
        #set data for pen p1 as original summed spectrum with no processing
        self.p1.setData(y=np.real(self.specoblist[self.curobject].OriginalSpectrum))
        #Markers will show bounds of phasing area
        x1_marker = np.ones(2)
        x2_marker = np.ones(2)
        y_marker = np.ones(2)
        #get min and max of spectrum for y marker
        y_marker[0] = min(np.real(self.specoblist[self.curobject].OriginalSpectrum))
        y_marker[1] = max(np.real(self.specoblist[self.curobject].OriginalSpectrum))
        #Get phase limits for x marker
        x1_marker[0] = self.specoblist[self.curobject].plim_l
        x1_marker[1] = self.specoblist[self.curobject].plim_l
        x2_marker[0] = self.specoblist[self.curobject].plim_r
        x2_marker[1] = self.specoblist[self.curobject].plim_r
        #Set pens p2 and p3 as the phase area limits
        self.p2.setData(x1_marker, y_marker)
        self.p3.setData(x2_marker, y_marker)
        self.PlotType = 1
        textout = 'Original Spectrum: ' + self.specoblist[self.curobject].filename
        self.lbl3.setText(textout)
        self.lbl3.adjustSize()

    #Plot processed spectrum in main window
    def plotprocspec(self):
        self.p1.clear()
        self.p2.clear()
        self.p3.clear()
        #set data for pen p1 as processed summed spectrum with no processing
        self.p1.setData(y=np.real(self.specoblist[self.curobject].FinalSpectrumauto))
        #Markers will show bounds of phasing area
        x1_marker = np.ones(2)
        x2_marker = np.ones(2)
        y_marker = np.ones(2)
        #get min and max of spectrum for y marker
        y_marker[0] = min(np.real(self.specoblist[self.curobject].FinalSpectrumauto))
        y_marker[1] = max(np.real(self.specoblist[self.curobject].FinalSpectrumauto))
        #Get phase limits for x marker
        x1_marker[0] = self.specoblist[self.curobject].plim_l
        x1_marker[1] = self.specoblist[self.curobject].plim_l
        x2_marker[0] = self.specoblist[self.curobject].plim_r
        x2_marker[1] = self.specoblist[self.curobject].plim_r
        self.p2.setData(x1_marker, y_marker)
        self.p3.setData(x2_marker, y_marker)
        self.PlotType = 1
        textout = 'Processed Spectrum: ' + self.specoblist[self.curobject].filename
        self.lbl3.setText(textout)
        self.lbl3.adjustSize()
        



    def Phasereg(self):
        leftinit = self.specoblist[self.curobject].plim_l
        rightinit = self.specoblist[self.curobject].plim_r
        adopinit = self.specoblist[self.curobject].adop_const
        dialog = PhaseDialog(leftinit, rightinit, adopinit)
        if dialog.exec_():
            leftlim = dialog.leftlim.text()        
            rightlim = dialog.rightlim.text()
            adop_const = dialog.adop_const.text()
            
        try:
            left_int = int(leftlim)
        except:
            left_int = leftinit
            
        try:
            right_int = int(rightlim)
        except:
            right_int = rightinit  
            
        try:
            adop_int = int(adop_const)
        except:
            adop_int = adopinit  
            
        self.specoblist[self.curobject].plim_l = left_int
        self.specoblist[self.curobject].plim_r = right_int 
        self.specoblist[self.curobject].adop_const = adop_int
        
        self.specoblist[self.curobject].autophase()

           
            
    def savedir(self):
        self.savedirname = str(QtGui.QFileDialog.getExistingDirectory(self,
                'Save Directory', 'S:\\Neonate_data\\3T\\PA'))
        textout = 'Save directory name: ' + self.savedirname
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


    def jmrui(self):
        if self.setsavedir == 0:
            self.savedir()
        self.specoblist[self.curobject].writejmruidata2(self.savedirname)

    def Tarquin(self):
        if self.setsavedir == 0:
            self.savedir()
        self.specoblist[self.curobject].writeTarquin(self.savedirname)
        
        
    def convert_to_all(self):
        if self.setsavedir == 0:
            self.savedir()
        self.specoblist[self.curobject].writejmruidata2orig(self.savedirname)
        self.specoblist[self.curobject].writeTarquinorig(self.savedirname)
        self.specoblist[self.curobject].writejmruidata2(self.savedirname)
        self.specoblist[self.curobject].writeTarquin(self.savedirname)
        self.specoblist[self.curobject].writelogfile(self.savedirname, self.version)
        self.specoblist[self.curobject].fitTarquin(self.savedirname)
        #self.plotfit()
        
    def Tarquinorig(self):
        if self.setsavedir == 0:
            self.savedir()
        self.specoblist[self.curobject].writeTarquinorig(self.savedirname)

    def frameup(self):
        self.specoblist[self.curobject].frameup()
        self.plotframe()
        
    def framedown(self):
        self.specoblist[self.curobject].framedown()
        self.plotframe()

    def plotframe(self):
        self.p21.setData(y=np.real(self.specoblist[self.curobject].current_frame))
        cur_frame = self.specoblist[self.curobject].curframe
            
        x1_marker = np.ones(2)
        x2_marker = np.ones(2)
        y_marker = np.ones(2)
        y_marker[0] = min(np.real(self.specoblist[self.curobject].current_frame))
        y_marker[1] = max(np.real(self.specoblist[self.curobject].current_frame))
        x1_marker[0] = self.specoblist[self.curobject].peakposarr[cur_frame][0]
        x1_marker[1] = self.specoblist[self.curobject].peakposarr[cur_frame][0]
        x2_marker[0] = self.specoblist[self.curobject].peakposarr[cur_frame][1]
        x2_marker[1] = self.specoblist[self.curobject].peakposarr[cur_frame][1]
        self.p22.setData(x1_marker, y_marker)
        self.p23.setData(x2_marker, y_marker)        
        
        
        if self.specoblist[self.curobject].IncludeFrame[cur_frame] == 1:
            textout = 'Include Frame: ' + str(cur_frame) + ' :' +str(self.specoblist[self.curobject].PatName)
        else:
            textout = 'Exclude Frame: ' + str(cur_frame) + ' :' +str(self.specoblist[self.curobject].PatName)
        self.lbl5.setText(textout)
        self.lbl5.adjustSize()     

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

        textout = 'Include Frame: ' + str(cur_frame) + ' :' +str(self.specoblist[self.curobject].PatName)
        self.lbl5.setText(textout)
        self.lbl5.adjustSize() 
        self.specoblist[self.curobject].addframes()
        

    def ExcFrame(self):
        cur_frame = self.specoblist[self.curobject].curframe
        self.specoblist[self.curobject].IncludeFrame[cur_frame] = 0
        textout = 'Exclude Frame: ' + str(cur_frame) + ' :' +str(self.specoblist[self.curobject].PatName)
        self.lbl5.setText(textout)
        self.lbl5.adjustSize() 
        self.specoblist[self.curobject].addframes()      

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
            self.p1.clear()
            self.p2.clear()
            self.p3.clear()
            self.p1.setData(Data_arr)
            self.p2.setData(Fit_arr)
        except:
            dummy = 1
                         
                        
                        




        
class PhaseDialog(QtGui.QDialog):
    
    def __init__(self, leftinit, rightinit, adop_const, parent = None):
        super(PhaseDialog, self).__init__(parent)
        self.left_string = str(leftinit)
        self.right_string = str(rightinit)
        self.adop_string = str(adop_const)
        
        rightlabel = QtGui.QLabel("&Right Limit:")
        self.rightlim = QtGui.QLineEdit(self.right_string)
        rightlabel.setBuddy(self.rightlim)

        leftlabel = QtGui.QLabel("&Left Limit:")
        self.leftlim = QtGui.QLineEdit(self.left_string)
        leftlabel.setBuddy(self.leftlim)

        adoplabel = QtGui.QLabel("&Adopisation:")
        self.adop_const = QtGui.QLineEdit(self.adop_string)
        adoplabel.setBuddy(self.adop_const)
        
        buttonbox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Cancel)
        buttonbox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        grid = QtGui.QGridLayout()
        grid.addWidget(leftlabel, 0,0)
        grid.addWidget(self.leftlim, 0,1)
        grid.addWidget(rightlabel, 1,0)
        grid.addWidget(self.rightlim, 1,1)
        grid.addWidget(adoplabel, 2,0)
        grid.addWidget(self.adop_const, 2,1)
        grid.addWidget(buttonbox, 4,0,3,2)
        self.setLayout(grid)
        self.connect(buttonbox, QtCore.SIGNAL("accepted()"), self, QtCore.SLOT("accept()"))
        #self.buttonbox.QtCore.SIGNAL("accepted()").connect(QtCore.SLOT("accept()"))

        
        self.setWindowTitle("Enter Limits")           
        
        
        
        
        
        

        
        
        
#Main function - needed to run script        
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = Maingui()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()