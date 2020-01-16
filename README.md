# MRS_Convert.py

Version 1.3.1
Modified 28/07/2017

Script to convert Philips MRS data to tarquin format for spectral processing
This script will deal with data acquired with multiple dynamic acquisitions
and saved in DICOM4 format. Phasing and peak picking is done automatically but
can be adjusted manually

Created on Thu Oct 01 11:36:59 2015

@author: Alan Bainbridge

## Class definitions:

### Maingui(QtGui.QMainWindow):

DESCRIPTION:

The class Maingui() creates the main GUI using QMainWindow class' functionality in QtGui module.   
It adds two windows in which to dyspplay the NMR spectra, 

METHODS:  

Cho_dn: the function of this method    


### PhaseDialog(QtGui.QDialog):

DESCRIPTION:

PhaseDialog() class creates the dialogs for .



#### In module file Spec_Module.py: 
SpecObject(object)
PDF(FPDF)

#Main function - needed to run script        
def main():



### Description of import methods in Class 'Maingui':

### Methods of Class 'PhaseDialog':

### Description of methods in Spec
dir(sp.SpecObject)
['Choinc',
 'Crinc',
 'NumSpecObjects',
 'addframes',
 'autophase',
 'complex_data',
 'create_original',
 'fitTarquin',
 'framedown',
 'frameup',
 'phaseinc',
 'report_completed',
 'set_current_frame',
 'spectypes',
 'undophase',
 'undoshift',
 'writeTarquin',
 'writeTarquinorig',
 'writejmruidata2',
 'writejmruidata2orig',
 'writelogfile']
