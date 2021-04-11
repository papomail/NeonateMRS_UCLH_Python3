# -*- coding: utf-8 -*-
"""

Spec_Module

Version 1.4 
Modified 21/02/2020

Python3 version of the script. Converted from: Version 1.3.1

Created on 11 Dic 2019 @author: Patxi Torrealdea

...

Version 1.3.1
Modified 1/10/2015

Defines objects of class Spec_Module


Created on Thu Oct 01 11:41:45 2015

@author: Alan Bainbridge
"""
from past.utils import old_div
import pydicom as dcm
import numpy as np
import os as os
import csv as csv
from fpdf import FPDF
import datetime
import PyPDF2
from PyQt5 import QtGui, QtCore, QtWidgets
from pathlib import Path
import shutil 
import sys

#BASE_DIR = Path(__file__).parent.parent.parent
# BASE_DIR = Path(__file__).parent.parent
BASE_DIR = Path(__file__).parent

# BASE_DIR = Path.cwd()

# print(BASE_DIR)



ICONS_DIR= BASE_DIR / 'Icons' 
UCLH_header=ICONS_DIR / 'UCLH_header.png'
UCLH_header=str(UCLH_header.resolve())

UCLH_footer=ICONS_DIR / 'UCLH_footer.png'
UCLH_footer=str(UCLH_footer.resolve())

class SpecObject():
    NumSpecObjects = 0  #To keep track of how many spec objects there are
    
    spectypes = {0 : "Not a spectroscopy dataset", \
                 1 : "classic spectroscopy dataset", \
                 2 : "Enhanced spectroscopy dataset", \
                 3 : "Siemens IMA file", \
                 4 : "RDA file"}
    
    def __init__(self, filename, dirpass):
        
        self.filename = filename
        self.dirpass = dirpass
        # self.mruiload = 0
        self.plim_l = 1110
        self.plim_r = 1140
        self.apod_const = 128.0
        SpecObject.NumSpecObjects += 1        
        # print(filename)
        
        try:
            self.ds = dcm.read_file(self.filename)
        except:
            self.ds = []
            SpecObject.NumSpecObjects -= 1
            
        # If it is a DICOM4 MRS file, get data and useful parameters       
        if [0x5600,0x0020] in self.ds:
            self.isspec = 2
            self.PatName = self.ds.PatientName
            self.StudyDate = self.ds.StudyDate
            self.StudyTime = self.ds.StudyTime
            self.SeriesDate = self.ds.SeriesDate
            self.SeriesTime = self.ds.SeriesTime
            self.SpecData = self.ds[0x5600,0x0020].value
            self.Datapoints = self.ds.DataPointColumns
            self.SpectralWidth = self.ds.SpectralWidth
            self.TransmitterFrequency = self.ds.TransmitterFrequency
            #self.FieldStrength = self.ds[0x0018,0x0087].value
            self.FieldStrength = 3.0
            self.PatID = self.ds.PatientID
            self.AcquisitionDateTime = self.ds.AcquisitionDateTime
            self.ProtocolName = self.ds.ProtocolName            
            self.Frames = self.ds.NumberOfFrames
            self.displayTE = self.ds[0x2001, 0x1025].value
            self.curframe = 0
                      
        else:
            self.isspec = 0
            self.SpecData = []
     
        if self.isspec != 0:
            self.complex_data()
            
 

    #Form complex k-space data and FFT to complex spectra.  Apodise also.      
    def complex_data(self):
        #Set up arrays to store data and flags for each dynamic acquisition
        #Number of dynamic acquisitions = self.Frames
        self.Kspace = []        #To store raw K-space
        self.Kspacewrite = []        #To store raw K-space
        self.Kspaceapod = []    #To store apodised K-space
        self.Spectrum = []      #To store raw spectrum
        self.Spectrumapod = []  #To store apodised spectrum
        self.IncludeFrame = []  #To store include frame flags
              
        #Set up apodisation function
        #apod = 1 in range [0:512] pts
        #apod = decaying exponential thereafter (decay const = 64)
        #Note division by 64.0 and not 64
        #Need to do this otherwise you get rounded integers rather than float values
        apod = np.ones(shape = [int(self.Datapoints)], dtype = float)
        
        for cntexp in range(512, int(self.Datapoints)):
            apod[cntexp] = np.exp(old_div(-(cntexp-512),self.apod_const))
        self.apod = apod

        #Loop through each frame
        for b in range(0, self.Frames):
            counter = 0
            #Set up dammy arrays to temporarily hold K-space and apodised K-space
            #data for an individual frame
            dummyKspace = np.zeros(shape = [self.Datapoints], dtype = complex)
            dummyKspaceapod = np.zeros(shape = [self.Datapoints], dtype = complex)
            
            #Data are store R,I,R,I,... in self.SpecData.  Loop through and 
            #extract R and I data pairs and then store as an array of complex
            #numbers of size self.Datapoints
            for a in range(0, self.Datapoints*2, 2):
                dummyKspace[counter] = complex(self.SpecData[(b*self.Datapoints*2) + a], self.SpecData[(b*self.Datapoints*2)+a+1])
                #dummyKspaceapod[counter] = dummyKspace[counter] * apod[counter]
                counter  = counter + 1

            #Apply apodisation 
            dummyKspaceapod = dummyKspace * self.apod
            
            #Append apodised and non-apodised k-space data to appropriate array
            self.Kspace.append(dummyKspace)
            self.Kspacewrite.append(dummyKspace)
            self.Kspaceapod.append(dummyKspaceapod)
            
            #For each frame, fft and fftshift to display spectrum propoerly
            dummyspectrum = np.fft.fftshift(np.fft.fft(np.conj(dummyKspace)))
            dummyspectrumapod = np.fft.fftshift(np.fft.fft(np.conj(dummyKspaceapod)))
            
            #Append apodised and non-apodised spectra to appropriate array
            self.Spectrum.append(dummyspectrum)
            self.Spectrumapod.append(dummyspectrumapod)
            
            #At this point all data are included (so =1)
            self.IncludeFrame.append(1)
            
            #Sum frames together to yield un-processed dataset
        self.create_original()
        self.autophase()
 
           
    #Add together individual frames to yield original summed datasets
    def create_original(self):
        self.OriginalKspace = np.zeros(shape = [self.Datapoints], dtype = complex)
        self.OriginalSpectrum = np.zeros(shape = [self.Datapoints], dtype = complex)
        if self.Frames == 1:
            frames = 1
        else:
            frames = old_div(self.Frames,2) #self.Frames / 2 because NWS data also stored in Dicom file
        for cnt in range(0, frames):
            self.OriginalKspace = self.OriginalKspace + self.Kspace[cnt]
            self.OriginalSpectrum = self.OriginalSpectrum + self.Spectrum[cnt]
            
            
            
    #Do Autophasing of individual frames        
    def autophase(self):
        #Create data array to store processed spectrum and k-space
        self.FinalKspaceauto = np.zeros(shape = [self.Datapoints], dtype = complex)
        self.FinalSpectrumauto = np.zeros(shape = [self.Datapoints], dtype = complex)
        
        #Create list for frame data
        self.Spectrumauto = []
        self.Spectrumautoapod = []
        if self.Frames == 1:
            frames = 1
        else:
            frames = old_div(self.Frames,2) #self.Frames / 2 because NWS data also stored in Dicom file
        
        #Set lists
        self.optphasearr = []  #Store phasing angle for each frame
        self.peakposarr = []
        # self.shiftarr = []
        # self.shiftindex = []
        self.curcomplex = []
        self.acurcomplex = []
        # self.med = []

        
        #First do the phasing
        for cnt in range(0, frames):
            self.FinalKspaceauto = self.FinalKspaceauto + self.Kspace[cnt]
            
            #Only use data in pre-set phasing range
            #Get initial mag and phase data
            curmag = np.abs(self.Spectrumapod[cnt][self.plim_l:self.plim_r])
            curangle = np.angle(self.Spectrumapod[cnt][self.plim_l:self.plim_r])
        
            #Going to loop through 0-360
            #apply phase shift and then cal diff between magnitude and real data
            phaselog = []
            for cntr in range(0, 360):
                curangle2 = curangle + (old_div(cntr*np.pi,180))
                curreal = curmag * np.cos(curangle2)
                curdiff = np.power((curmag - curreal),2)
                phaselog.append(np.sum(curdiff))
            
            #optimum phase shift where difference is minimised
            optphase = np.argmin(np.array(phaselog))
            
            #Apply optimum phase shift to whole spectrum
            curmagf = np.abs(self.Spectrum[cnt])
            curanglef = np.angle(self.Spectrum[cnt])
            curangle2f = curanglef + (old_div(optphase*np.pi,180)) 
            currealf = curmagf * np.cos(curangle2f)
            curimagf = curmagf * np.sin(curangle2f)
            self.curcomplex.append(currealf + 1j*curimagf)

            #Apply optimum phase shift to apodised whole spectrum            
            acurmagf = np.abs(self.Spectrumapod[cnt])
            acuranglef = np.angle(self.Spectrumapod[cnt])
            acurangle2f = acuranglef + (old_div(optphase*np.pi,180)) 
            acurrealf = acurmagf * np.cos(acurangle2f)
            acurimagf = acurmagf * np.sin(acurangle2f)
            self.acurcomplex.append(acurrealf + 1j*acurimagf)            
            
            #store optiumum phase shift in list
            self.optphasearr.append(optphase)
            
            

            #Add in auto pick of peaks ---------------------------
            #Looking for Cho and Cr peaks

            #Flag to indicate if peaks have been found
            got_peaks = 0
            
            #Going to start at max height of real spec and then increment 
            #downwards until wee hit a peak
            #Do this within the expected range for Cho and Cr peaks
            max_height = np.max(currealf)
            inc = old_div(max_height,100)    #increment size
            thresh = 0
            while got_peaks < 1:
                found_peaks = 0
                peak_pos = []
                for cntr in range(1100,1160):
                    if currealf[cntr] > thresh:
                        local = currealf[cntr-5:cntr+6]
                        if np.argmax(local) == 5:
                            found_peaks = found_peaks + 1
                            peak_pos.append(cntr)
                            
                if found_peaks > 2:
                    thresh = thresh + inc
                else:
                    got_peaks = 1
            
                        
            if np.size(peak_pos) < 2:
                peak_pos = []
                peak_pos.append(1120)
                peak_pos.append(peak_pos[0] + 10)
            #Store peak position arrays for each frame in a list
            self.peakposarr.append(peak_pos)
            

        
        self.addframes()


    #Add frames together        
    def addframes(self):
        self.FinalKspaceauto = np.zeros(shape = [self.Datapoints], dtype = complex)
        self.FinalSpectrumauto = np.zeros(shape = [self.Datapoints], dtype = complex)
        self.med = []
        self.shiftindex = []
        
        if self.Frames == 1:
            frames = 1
        else:
            frames = old_div(self.Frames,2) #self.Frames / 2 because NWS data also stored in Dicom file

        for cnt in range(0, frames): 
            #Store the mid point between the peaks in a list
            #If something goes wrong then a value of zero is stored
            
            '''Remove try/if block & include negative values to the median   Patxi'''
            # try:
            #     ind = np.int(np.floor(old_div((self.peakposarr[cnt][0] + self.peakposarr[cnt][1]),2))) 
            #     self.shiftindex.append(ind)
            # except:
            #     ind = 0
            #     self.shiftindex.append(ind)
                
            # if ind > 0:
            #     self.med.append(ind)  
            
            ind = np.int(np.floor(old_div((self.peakposarr[cnt][0] + self.peakposarr[cnt][1]),2))) 
            self.shiftindex.append(ind)
            self.med.append(ind) 


        # print(self.med)
        med_shift_index = np.floor(np.median(self.med))
        # print('median shift index:' + str(med_shift_index))
      
        
        for cnt in range(0, frames): 
            if self.IncludeFrame[cnt] == 1: 
                shift = int(med_shift_index - self.shiftindex[cnt])
                #print shift
                addcomplex = np.roll(self.curcomplex[cnt], shift)
                #addcomplex = np.roll(self.acurcomplex[cnt], shift) #Patxi

                #self.Kspace[cnt] = np.fft.ifft(np.fft.fftshift(curcomplex[cnt]))
                self.Kspacewrite[cnt] = np.fft.ifft(np.fft.fftshift(addcomplex))
                self.FinalSpectrumauto = self.FinalSpectrumauto + addcomplex 
            else:
                #self.Kspace[cnt] = np.fft.ifft(np.fft.fftshift(curcomplex[cnt]))
                self.Kspacewrite[cnt] = np.zeros(shape = [self.Datapoints], dtype = complex)
            self.Spectrumauto.append(self.curcomplex[cnt])
            self.Spectrumautoapod.append(self.acurcomplex[cnt]) #Patxi
        self.set_current_frame()
        
        #IFT to get time domain data
        self.FinalKspaceauto = np.fft.ifft(np.fft.fftshift(self.FinalSpectrumauto))

        #self.shiftapod()

    def phaseinc(self, increment):
        #Apply optimum phase shift to whole spectrum
        curmagf = np.abs(self.curcomplex[self.curframe])
        curanglef = np.angle(self.curcomplex[self.curframe])
        curangle2f = curanglef + (old_div(increment*np.pi,180)) 
        currealf = curmagf * np.cos(curangle2f)
        curimagf = curmagf * np.sin(curangle2f)
        temp_complex = currealf + 1j*curimagf        
        self.curcomplex[self.curframe] = temp_complex
        
        #Apply optimum phase shift to apodised whole spectrum            
        acurmagf = np.abs(self.acurcomplex[self.curframe])
        acuranglef = np.angle(self.acurcomplex[self.curframe])
        acurangle2f = acuranglef + (old_div(increment*np.pi,180)) 
        acurrealf = acurmagf * np.cos(acurangle2f)
        acurimagf = acurmagf * np.sin(acurangle2f)
        atemp_complex = acurrealf + 1j*acurimagf
        self.acurcomplex[self.curframe] = atemp_complex
        
        #Modify storage of phasing angle for current frame
        self.optphasearr[self.curframe] = self.optphasearr[self.curframe] + increment
        self.addframes()
        self.set_current_frame()

    def Choinc(self, increment):
        #Apply optimum phase shift to whole spectrum
        temp_ppa = self.peakposarr[self.curframe]
        temp_ppa[0] = temp_ppa[0] + increment
        self.peakposarr[self.curframe] = temp_ppa
        self.addframes()
        self.set_current_frame()

    def Crinc(self, increment):
        #Apply optimum phase shift to whole spectrum
        temp_ppa = self.peakposarr[self.curframe]
        temp_ppa[1] = temp_ppa[1] + increment
        self.peakposarr[self.curframe] = temp_ppa
        self.addframes()
        self.set_current_frame()

    def framedown(self):
        if self.curframe > 0:
            self.curframe -= 1
        self.set_current_frame()
      
    def frameup(self):
        if self.curframe < ((old_div(self.Frames,2)) - 1):
            self.curframe += 1
        self.set_current_frame()
            
    def set_current_frame(self):
        self.current_frame = self.acurcomplex[self.curframe]
        #self.current_frame = self.Spectrumautoapod[self.curframe]
        #print self.peakposarr[self.curframe]
        #print self.shiftindex[self.curframe]
        




    def writeTarquin(self, outpath):
        #Tarquindir = outpath + '\\' + 'Tarquin_files'
        outpath=Path(outpath)
        Tarquindir = outpath / 'Tarquin_files'

        # if os.path.isdir(Tarquindir) == False:
        #     os.chdir(outpath)
        #     os.mkdir('Tarquin_files')
        Tarquindir.resolve().mkdir(parents=True, exist_ok=True)


        name = self.filename[(self.filename.rfind('\\')+1):].translate(str.maketrans('','', r'.'))
        #file_path = Tarquindir + '\\' + self.dirpass + '__' + name + 'proc_Tarquin'
        file_path = Path(Tarquindir , name + 'proc_Tarquin')
        print(file_path)
        
        Spec_temp = self.SpecData
        counter = 0
        
        #Need complex conj for proper display, hence -imag
        for b in range(0,old_div(self.Frames,2)):
            for a in range(0, self.Datapoints):
                Spec_temp[counter] = self.Kspacewrite[b][a].real 
                counter = counter + 1
                Spec_temp[counter] = -self.Kspacewrite[b][a].imag 
                counter = counter + 1
                
        self.ds[0x5600,0x0020].value = Spec_temp  
        self.ds.save_as(str(file_path.resolve()))
 
       
        
    def undophase(self):    
        self.curcomplex = self.Spectrum
        self.acurcomplex = self.Spectrumapod
        
        if self.Frames == 1:
            frames = 1
        else:
            frames = old_div(self.Frames,2) #self.Frames / 2 because NWS data also stored in Dicom file
        #Reset store of phasing angle for each from to zero
        for cnt in range(0, frames): 
            self.optphasearr[cnt] = 0            
            
        self.addframes()
        self.set_current_frame()
        
    def undoshift(self):    
        if self.Frames == 1:
            frames = 1
        else:
            frames = old_div(self.Frames,2) #self.Frames / 2 because NWS data also stored in Dicom file
        
        temp_ppa = [1020, 1030]
        for cnt in range(0, frames): 
            self.peakposarr[cnt] = temp_ppa
            
        self.addframes()
        self.set_current_frame()

    def report_completed(self,report_path):
        self.report_completed_msg=f'MRS Report saved in {report_path}'


    def writelogfile(self, outpath, version):
        outpath=Path(outpath)
        #Logdir = outpath + '\\' + 'Log_files'
        Logdir = outpath / 'Log_files'

        # if os.path.isdir(Logdir) == False:
        #     os.chdir(outpath)
        #     os.mkdir('Log_files')
        Logdir.resolve().mkdir(parents=True, exist_ok=True)

        if self.Frames == 1:
            frames = 1
        else:
            frames = old_div(self.Frames,2) #self.Frames / 2 because NWS data also stored in Dicom file
                
        name = self.filename[(self.filename.rfind('\\')+1):].translate(str.maketrans('','', r'.'))
        #file_path = Logdir + '\\' + self.dirpass + '__' + name + 'log_file.txt'  
        file_path = Path(Logdir , name + 'log_file.txt'  )
         
        #self.text_file = open(file_path, 'w')
        self.text_file = open(str(file_path.resolve()), 'w')

         # Write Log File
        self.text_file.write('Tarquin Pre-processing Log file\n\n')
        print('Filename: %s\n' % (file_path), file=self.text_file)
        print('Version: %s\n' % (version), file=self.text_file)
        
        for cnt in range(0, frames):
            print('Frame: %i' % (cnt), file=self.text_file)
            print('Include: %i' % (self.IncludeFrame[cnt]), file=self.text_file)
            print('Phasing: %i' % (self.optphasearr[cnt]), file=self.text_file)
            intostr = 'Peak positions: ' + str(self.peakposarr[cnt]) 
            self.text_file.write(intostr + '\n\n')

        self.text_file.close()
        print('Log file written')
        
    def fitTarquin(self, outpath):
        nameinit = self.PatName
        dialog = PatNameDialog(nameinit)
        if dialog.exec_():
            name = dialog.name.text()        

            
        try:
            self.PatName = name
        except:
            self.PatName = nameinit        
        
        outpath=Path(outpath)
        #Tarquindir = outpath + '\\' + 'Tarquin_files'
        Tarquindir = outpath / 'Tarquin_files'
        name = self.filename[(self.filename.rfind('\\')+1):].translate(str.maketrans('','', r'.'))
        filename =  name + 'proc_Tarquin'
        #file_path = Tarquindir + '\\' + filename
        file_path = str(Path(Tarquindir , filename).resolve())
        
        #Tarquinfitdir = Tarquindir + '\\' + 'Tarquin_fit'
        Tarquinfitdir = Tarquindir / 'Tarquin_fit'

        # if os.path.isdir(Tarquinfitdir) == False:
        #     os.chdir(Tarquindir)
        #     os.mkdir('Tarquin_fit')
        #    
        Tarquinfitdir.resolve().mkdir(parents=True, exist_ok=True)


            
        # reportout = Tarquinfitdir + '\\' + self.PatName + '_Report.pdf'
        # tempout = Tarquinfitdir + '\\' + filename + '_temp.pdf'
        # pdfout = Tarquinfitdir + '\\' + filename + '_plot.pdf'
        # dataout = Tarquinfitdir + '\\' + filename + '_data.csv'
        # moddataout = Tarquinfitdir + '\\' + filename + '_data_with_ratios.csv'
        # resout = Tarquinfitdir + '\\' + filename + '_results.csv'
        # self.fitout = Tarquinfitdir + '\\' + filename + '_fit.txt'
        # basis = 'S:\\Neonate_data\\Tarquin\\3_0T_basis_threonine_no_MM'
        # tarquin = 'S:\\Neonate_data\\Tarquin\\TARQUIN_Windows_4.3.7\\tarquin\\tarquin'

        reportout = str(Path(Tarquinfitdir , str(self.PatName) + '_Report.pdf').resolve())
        #reportout = Path(Tarquinfitdir , self.PatName + '_Report.pdf')
        tempout = str(Path(Tarquinfitdir ,filename + '_temp.pdf').resolve())
        pdfout = str(Path(Tarquinfitdir , filename + '_plot.pdf').resolve())
        dataout = str(Path(Tarquinfitdir , filename + '_data.csv').resolve())
        moddataout = str(Path(Tarquinfitdir , filename + '_data_with_ratios.csv').resolve())
        resout = str(Path(Tarquinfitdir , filename + '_results.csv').resolve())
        self.fitout = str(Path(Tarquinfitdir , filename + '_fit.txt').resolve())

        basis = str(Path(BASE_DIR ,'3_0T_basis_threonine_no_MM').resolve())
        print(f'basis: {basis}')
        
        if sys.platform == "darwin":
            tarquin_path=Path(BASE_DIR ,'TARQUIN/mac/tarquingui.app/Contents/MacOS/tarquin')
        elif sys.platform == "win32":   
            tarquin_path=Path(BASE_DIR ,'TARQUIN/win/TARQUIN_Windows_4.3.10/tarquin/tarquin.exe')
        elif sys.platform == "linux":   
            tarquin_path=Path(BASE_DIR ,'TARQUIN/linux/tarquin')

        
        if tarquin_path.exists():
            tarquin = str(tarquin_path.resolve())    
        elif shutil.which("tarquin"):
            tarquin = shutil.which("tarquin")
        else:
            error=f'\nTarquin not found. \nTo solve it please:\n a) copy the Tarquin app inside {BASE_DIR} folder, or\n b) add Tarquin to the Path. e.g. >> export PATH=$PATH:/Applications/tarquingui.app/Contents/MacOS\n'
            print(error)
            sys.exit(error)

  
        command =  (tarquin + ' --input ' + file_path + ' --output_pdf ' +  pdfout + 
            ' --output_csv ' + dataout + ' --output_fit ' + self.fitout  +
            ' --basis_csv ' + basis)


        # run the command 
        print('this the the command for tarquin: ',command) 
        os.system(command)
        
        #Add in sode code to automatically calculate the Lac/Naa ratio
        #Note that this will assume that the correct basis set is used
        #csvfile = open(dataout, 'rb')
        
        with open(dataout) as csvfile:
            linereader = csv.reader(csvfile, delimiter = ',')
            CSVstore = []
        
            counter = 0
            for row in linereader:
                counter += 1
                # print(row)

                if counter == 2:
                    row.append('Lac+T/tNaa')
                    row.append('tNaa/tCho')
                    row.append('tNaa/Cr')
                    row.append('tCho/Cr')
                    row.append('Lac+T/tCho')
                    row.append('Lac+T/Cr')
                
                if counter == 5:
                    row.append('Lac+T/tNaa')
                    row.append('tNaa/tCho')
                    row.append('tNaa/Cr')
                    row.append('tCho/Cr')
                    row.append('Lac+T/tCho')
                    row.append('Lac+T/Cr')
            #Calc ratio        
                if counter == 3:
                    #dummy = str(row)
                    #dummy = dummy.translate(None, ''.join(["[", "'", "]"]))
                  
                    #print('dummy is: ',dummy)
                    
                    #fields = dummy.split(', ')
                    fields = row
                    
                    # print('type of fields[14] is: ',type(fields[14]))
                    # print('fields[14] is: ',fields[14])
                    
                    Lac = np.float(fields[14])
                    Naa =  np.float(fields[15])
                    NaaG =  np.float(fields[16])
                    Thre = np.float(fields[21])
                    Cr = np.float(fields[6])
                    tCho = np.float(fields[23])
                    L_N = old_div((Lac + Thre), (Naa + NaaG))
                    N_Ch = old_div((Naa + NaaG), tCho)
                    N_Cr = old_div((Naa + NaaG), Cr)
                    Ch_Cr = old_div(tCho, Cr)
                    L_Ch = old_div((Lac + Thre), tCho)
                    L_Cr = old_div((Lac + Thre), Cr)
                    row.append(str(L_N))
                    row.append(str(N_Ch))
                    row.append(str(N_Cr))
                    row.append(str(Ch_Cr))
                    row.append(str(L_Ch))
                    row.append(str(L_Cr))
            
            #calc error        
                if counter == 6:
                    dummy = str(row)
                    # #dummy = dummy.translate(None, ''.join(["[", "'", "]"]))
                    #dummy = dummy.translate(''.join(["[", "'", "]"]))
                    fields = row
                    Lace = np.float(fields[14])
                    Naae =  np.float(fields[15])
                    NaaGe =  np.float(fields[16])
                    Three = np.float(fields[21])
                    Cre = np.float(fields[6])
                    tChoe = np.float(fields[23])
                    
                    Lerr = np.sqrt(np.power(Lace,2) + np.power(Three,2))
                    Nerr = np.sqrt(np.power(Naae,2) + np.power(NaaGe,2))
                    L_Ne = np.sqrt(np.power(old_div(Lerr,(Lac + Thre)),2) + np.power(old_div(Nerr,(Naa + NaaG)), 2)) * L_N
                    N_Che = np.sqrt(np.power(old_div(Nerr,(Naa + NaaG)),2) + np.power(old_div(tChoe,(tCho)), 2)) * N_Ch
                    N_Cre = np.sqrt(np.power(old_div(Nerr,(Naa + NaaG)),2) + np.power(old_div(Cre,(Cr)), 2)) * N_Cr
                    Ch_Cre = np.sqrt(np.power(old_div(tChoe,(tCho)),2) + np.power(old_div(Cre,(Cr)), 2)) * Ch_Cr
                    L_Che = np.sqrt(np.power(old_div(Lerr,(Lac + Thre)),2) + np.power(old_div(tChoe,(tCho)), 2)) * L_Ch
                    L_Cre = np.sqrt(np.power(old_div(Lerr,(Lac + Thre)),2) + np.power(old_div(Cre,(Cr)), 2)) * L_Cr
                    row.append(str(L_Ne))
                    row.append(str(N_Che))
                    row.append(str(N_Cre))
                    row.append(str(Ch_Cre))
                    row.append(str(L_Che))
                    row.append(str(L_Cre))
                    
            #get FWHM and SNR
                if counter == 9:
                    #dummy = str(row)
                    #dummy = dummy.translate(''.join(["[", "'", "]"]))
                    #fields = dummy.split(", ")
                    fields = row
                    FWHM = np.float(fields[7])
                    SNR =  np.float(fields[9])
            
            
                CSVstore.append(row)
                #linewriter.writerow(row)
                #    
            #csvfile.close()
        
        
        resultsout = open(resout, 'w')
        line1 = 'Ratio, Value, Error, Proc FWHM, Proc SNR'
        # print(line1)
        line2 = 'L+T/tNaa,' + str(L_N) + ',' + str(L_Ne) + ',' + str(FWHM) + ',' + str(SNR)
        line3 = 'tNaa/tCho,' + str(N_Ch) + ',' + str(N_Che)
        line4 = 'tNaa/Cr,' + str(N_Cr) + ',' + str(N_Cre)
        line5 = 'tCho/Cr,' + str(Ch_Cr) + ',' + str(Ch_Cre)
        line6 = 'L+T/tCho,' + str(L_Ch) + ',' + str(L_Che)
        line7 = 'L+T/Cr,' + str(L_Cr) + ',' + str(L_Cre)
        resultsout.write(line1)
        resultsout.write('\n')
        resultsout.write(line2)
        resultsout.write('\n')
        resultsout.write(line3)
        resultsout.write('\n')
        resultsout.write(line4)
        resultsout.write('\n')
        resultsout.write(line5)
        resultsout.write('\n')
        resultsout.write(line6)
        resultsout.write('\n')
        resultsout.write(line7)
        
        resultsout.close()
        
        csvout = open(moddataout, 'w')
        for line in CSVstore:
            c = str(line)
            #line2 = c.translate(None, ''.join(["[", "'", "]"]))
            line2 = c.translate(''.join(["[", "'", "]"]))
            #print line2
            csvout.write(line2)
            csvout.write('\n')
        
        csvout.close() 


        pdf = PDF()
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        titleout = 'Spectroscopy Report for ' + str(self.PatName)
        pdf.cell(0,0, titleout, 0,0,'C')
        pdf.ln(15)
        
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(10)
        pdf.cell(0,0, 'Metabolite Ratios', 0,0,'L')
        
        pdf.ln(5)
        pdf.cell(10)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(20,10, 'Ratio', 1,0,'C')
        pdf.cell(25,10, 'tNaa/tCho', 1,0,'C')
        pdf.cell(25,10, 'tNaa/Cr', 1,0,'C')
        pdf.cell(25,10, 'tCho/Cr', 1,0,'C')
        pdf.cell(25,10, 'L+T/tCho', 1,0,'C')
        pdf.cell(25,10, 'L+T/Cr', 1,0,'C')
        pdf.cell(25,10, 'L+T/tNaa', 1,1,'C')
        
        pdf.cell(10)
        pdf.cell(20,10, 'Value', 1,0,'C')
        pdf.set_font('Arial', '', 10)
        textout = str(round(N_Ch, 2))
        pdf.cell(25,10, textout, 1,0,'C')
        textout = str(round(N_Cr, 2))
        pdf.cell(25,10, textout, 1,0,'C')
        textout = str(round(Ch_Cr, 2))
        pdf.cell(25,10, textout, 1,0,'C')
        textout = str(round(L_Ch, 2))
        pdf.cell(25,10, textout, 1,0,'C')
        textout = str(round(L_Cr, 2))
        pdf.cell(25,10, textout, 1,0,'C')
        pdf.set_font('Arial', 'B', 12)
        textout = str(round(L_N, 2))
        pdf.cell(25,10, textout, 1,1,'C')
        
        pdf.cell(10)
        pdf.cell(20,10, 'Error', 1,0,'C')
        pdf.set_font('Arial', '', 10)
        textout = str(round(N_Che, 2))
        pdf.cell(25,10, textout, 1,0,'C')
        textout = str(round(N_Cre, 2))
        pdf.cell(25,10, textout, 1,0,'C')
        textout = str(round(Ch_Cre, 2))
        pdf.cell(25,10, textout, 1,0,'C')
        textout = str(round(L_Che, 2))
        pdf.cell(25,10, textout, 1,0,'C')
        textout = str(round(L_Cre, 2))
        pdf.cell(25,10, textout, 1,0,'C')
        pdf.set_font('Arial', 'B', 12)
        textout = str(round(L_Ne, 2))
        pdf.cell(25,10, textout, 1,1,'C')
        
        pdf.ln(3)
        pdf.cell(10)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0,5, 'Notes:', 0,1,'L')
        pdf.set_font('Arial', '', 10)
        pdf.cell(10)
        pdf.cell(0,5, 'L+T = Lactate + Threonine.  Including Threonine yields a better fit at ~ 1.3 ppm', 0,1,'L')
        pdf.cell(10)
        pdf.cell(0,5, 'tNaa = Total Naa', 0,1,'L')
        pdf.cell(10)
        pdf.cell(0,5, 'tCho = Total Choline', 0,1,'L')
        pdf.cell(10)
        pdf.cell(0,5, 'Errors on ratios calculated using Cramer-Rao low bounds on Tarquin fit', 0,1,'L')
        
        pdf.ln(5)
        pdf.cell(10)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0,5, 'Some care must be taken when comparing Tarquin ratios to jMRUI ratios:', 0,1,'L')
        pdf.cell(10)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0,5, '1) Tarquin fits a complete basis spectrum for each metabolite whereas jMRUI fits individual peaks', 0,1,'L')
        pdf.cell(10)
        pdf.cell(0,5, '2) Tarquin effectively produces T2-weighted metabolite concentration ratios', 0,1,'L')
        pdf.cell(10)
        pdf.cell(0,5, '3) jMRUI effectively produces T2-weighted peak-area ratios', 0,1,'L')
        pdf.cell(10)
        pdf.cell(0,5, '4) The Choline peak has 9 equivalent protons whereas the other prominent peaks have only 3', 0,1,'L')
        pdf.cell(10)
        pdf.cell(0,5, '5) This means Tarquin ratios involving Choline are approximately a factor 3 different to jMRUI ratios', 0,1,'L')
        pdf.cell(10)
        pdf.cell(0,5, '6) When comparing Cho ratios to previous or published data please be careful of the methodologies used', 0,1,'L')
        pdf.cell(10)
        pdf.cell(0,5, '7) LCModel data will be similar to Tarquin', 0,1,'L')
        pdf.cell(10)
        pdf.cell(0,5, '8) If in doubt, please contact Medical Physics for help or clarification', 0,1,'L')
        
        pdf.ln(15)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(10)
        pdf.cell(0,0, 'Spectrum Quality Control', 0,0,'L')
        
        pdf.ln(5)
        pdf.cell(10)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(40,10, 'Proc FWHM', 1,0,'C')
        pdf.cell(40,10, 'Proc SNR', 1,0,'C')
        pdf.cell(40,10, 'Echo Time', 1,1, 'C')
        pdf.set_font('Arial', '', 10)
        pdf.cell(10)
        textout = str(round(FWHM, 2))
        pdf.cell(40,10, textout, 1,0,'C')
        textout = str(round(SNR, 2))
        pdf.cell(40,10, textout, 1,0,'C')
        pdf.cell(40,10, self.displayTE, 1,1,'C')
        
        pdf.ln(3)
        pdf.cell(10)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0,5, 'Notes:', 0,1,'L')
        pdf.set_font('Arial', '', 10)
        pdf.cell(10)
        pdf.cell(0,5, 'FWHM = Full Width Half Maximum: Measure of linewidth in ppm', 0,1,'L')
        pdf.cell(10)
        pdf.cell(0,5, 'SNR = Signal to Noise Ratio', 0,1,'L')
        
        pdf.output(tempout, 'F')
        
        # Merge PDF files
        pdfFileObj1 =open(tempout,'rb')
        pdfFileObj2 =open(pdfout,'rb')
        
        pdfReader1 = PyPDF2.PdfFileReader(pdfFileObj1)
        pdfReader2 = PyPDF2.PdfFileReader(pdfFileObj2)
        
        
        
        pageObj1 = pdfReader1.getPage(0)
        pageObj2 = pdfReader2.getPage(0)
        pageObj2.rotateClockwise(270)
        
        pdf_writer = PyPDF2.PdfFileWriter()
        pdf_writer.addPage(pageObj1)
        pdf_writer.addPage(pageObj2)
        
        
        pdf_out = open(reportout, 'wb')
        pdf_writer.write(pdf_out)
        pdf_out.close()
        
        pdfFileObj1.close()
        pdfFileObj2.close()
        
        
        print(f'\n\nMRS Report saved in {reportout}')
        self.report_completed(reportout)
        try:
            os.startfile
        except:     
            os.system(f'open {reportout}')



    




        
class PDF(FPDF):
   
    def header(self):
        
        # Logo
        self.image(UCLH_header, 120, 12, 80)
        # Arial bold 15
        self.set_font('Arial', '', 10)
        # Move to the right
        self.cell(10)
        # Title
        self.cell(0, 10, 'Section: MRI', 0, 1, 'L')
        self.cell(10)
        self.cell(0,0, 'Medical Physics and Biomedical Engineering', 0,0,'L')
        self.line(20,25,200,25)
        # Line break
        self.ln(15)

    # Page footer
    def footer(self):
        # Logo
       
        
        self.image(UCLH_footer, 20, 270, 160)
        #self.image('S:\\Alan_projects\\Logos_do_not_alter\\UCLH_Footer.png', 20, 270, 160)
        # Position at 1.5 cm from bottom
        self.set_y(-40)
        # Arial italic 8
        self.set_font('Arial', 'I', 10)
        # Footer
        self.cell(10)
        self.cell(45, 10, 'Neonatal MRS Report', 1, 0, 'C')
        #self.cell(90)
        self.cell(45, 10, 'Tarquin Version 4.3.11', 1, 0, 'C')
        i = datetime.datetime.now()
        datetext = 'Date: ' +str(i.day) + '/' + str(i.month) + '/' + str(i.year)
        self.cell(45,10, datetext, 1,0,'C')
        self.cell(45,10, 'Page 1 of 2', 1,0,'C')
 

class PatNameDialog(QtWidgets.QDialog):
    
    def __init__(self, nameinit, parent = None):
        super(PatNameDialog, self).__init__(parent)
        self.name_string = str(nameinit)

        
        namelabel = QtGui.QLabel("&Patient ID:")
        self.name = QtGui.QLineEdit(self.name_string)
        namelabel.setBuddy(self.name)
        
        #buttonbox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Cancel)
        self.buttonbox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        
        grid = QtGui.QGridLayout()
        grid.addWidget(namelabel, 0,0)
        grid.addWidget(self.name, 0,1)
        grid.addWidget(self.buttonbox, 2,0,3,2)

        self.setLayout(grid)
        
        #self.connect(buttonbox, SIGNAL(accepted()), self.name, SLOT(accept()))
        #self.connect(buttonbox, QtCore.SIGNAL("accepted()"), self, QtCore.SLOT("accept()"))
        #self.buttonbox.QtCore.SIGNAL("accepted()").connect(QtCore.SLOT("accept()"))
        #self.buttonbox.connect()
        #self.buttonbox.accepted.connect(QtCore.SLOT("accept()")
        self.buttonbox.accepted.connect(self.accept)

        self.setWindowTitle("Check Name")     



