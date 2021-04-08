# Neonate MRS UCLH (Python3)
#### The Department of Medical Physics and Biomedical Engineering at University College London Hospitals.
This repository contains the software used to process and produce automated reports of neonatal NMR spectra acquired at 3T MRI scanners at University College London Hospital.    



## Who is it for
This software is meant to be used by MRI Clinical Scientists. Its purpose is to assist in the processing of MRS data acquired @UCLH and to generate reports for the clinical team in a quick and robust manner. However, it does not exclude the need of MR expertise and knowledge of neonate MR spectroscopy for its correct use.  


* **This software is NOT intended as an unsupervised data processing solution.**    
* **Reports produced by this sofware must be approved by a MRI Clinical Scientist @UCLH**




# Installation
#### 1) Prerequisites:
NeonateMRS_UCLH_Python3 needs [Python 3](https://www.python.org/downloads/) and [TARQUIN](http://tarquin.sourceforge.net/index.php) software to work.  
* To check if you have the required versions of Python and TARQUIN installed, in a terminal run:    
`python3 -V`  (Python version should be <t>&ge;</t> 3.7)  
`tarquin` (TARQUIN version should be <t>&ge;</t> 4.3.10)

* If you need to install Python 3 or TARQUIN follow the links below:   
   - Download Python 3 from [here](https://www.python.org/downloads/) and follow the installation instructions.    
   - Download the latest binaries of TARQUIN from [here](https://sourceforge.net/projects/tarquin/files/).  
   ***Alternatively, you can download TARQUIN from one of the 'tarquin' branches of this repository, as shown below.*** 

#### 2) Installing NeonateMRS_UCLH_Python3:
* Clone or download this repository into a folder of your choosing, e.g. '~/projects':  
`mkdir ~/projets`  
`cd ~/projets`  
`git clone https://github.com/papomail/NeonateMRS_UCLH_Python3.git`    
    - To download TARQUIN together with NeonateMRS_UCLH_Python3, clone the 'tarquin_mac', 'tarquin_win' or 'tarquin_linux' branch instead. E.g. for Windows users type:   
`git clone -b tarquin_win https://github.com/papomail/NeonateMRS_UCLH_Python3.git`    

* Create and activate a virtual environment inside the newly cloned NeonateMRS_UCLH_Python3 folder (recommended):  
  *On Linux or macOS:*   
  `cd NeonateMRS_UCLH_Python3`   
  `python3 -m venv venv`   
  `source venv/bin/activate`    
  
  *On Windows:*   
  `cd NeonateMRS_UCLH_Python3`   
  `py -m venv venv`   
   `.\venv\Scripts\activate`   

* Upgrade *pip* and *setuptools* (recomended):   
  *On Linux or macOS:*     
  `python -m pip install --upgrade pip setuptools`  
  *On Linux or macOS:*   
  `py -m pip install --upgrade pip setuptools`      
  
* Install NeonateMRS_UCLH_Python3 module and requirements:  
  *On Linux or macOS:*     
  `python -m pip install -e . `   
  *On Windows:*   
  `python -m pip install -e . `     


# How to use it:
1) If NeonateMRS_UCLH_Python3 was installed in a virtual environment, remember to activate it:
   - In a terminal from the folder with the NeonateMRS_UCLH_Python3 script type:      
    *On Linux or macOS:*   
    `source venv/bin/activate`   
    *On Windows:*   
    `.\venv\Scripts\activate`   

2) Run **MRS_Convert.py** script:
   - Execute the main script by typing:   
    *On Linux or macOS:*    
    `python3 MRS_Convert.py`   
    *On Windows:*   
    `py MRS_Convert.py`   
     
     
3) Select *input folder* (with DICOM data) and the *output folder* (where proccesd data will be saved):    
    - From the menubar click on *File > Open Dir* to select folder with the DICOM files to analyse.  
    - From the menubar select also a folder where output of the code will be saved:   
File > Save Dir  

      <img src="Doc/openDir.png" width="200"> 

    (The actual PDF report will be saved in subfolder /Tarquin_files/Tarquin_fit/ inside the selected *output folder*).

3) Use buttons **Phase +/-** to phase the spectrum until the both Choline and Creatine resonance peaks are in pure absorption mode (both pointing up).
   
4) Use buttons **Peak1 +/-** and **Peak2 +/-** to move the red and green lines to centre of the Choline and Creatine resonance peaks, respectively.
    
5) Use buttons **F_up** and **F_down** to repeat steps 3 & 4 for all *frames*. (There are 16 *frames* in our current protocol).
   
6) If the spectrum of a particular *frame* is of bad quality (e.g. wider peaks, or lower SNR) and is considered that it would be detrimental to the quality of the final spectrum, use the **Exclude** button to avoid using the *current frame* in the analysis.  
(To reverse the process and use the **Include** button to include the *current frame* to the analysis).

    <img src="Doc/shift_frame2.png" width="500" height="450"> 

7) Once all the *frames* are checked, on the menubar press *Tools > Convert to JMRUI and Tarquin* to initiate the spectroscopic analysis and generate the PDF report.
   
    <img src="Doc/convert.png" width="300" > 

8) Open and review the PDF report (in subfolder /Tarquin_files/Tarquin_fit/).  
Check that the **peaks are well fitted**, the **echo time is 288 ms** and that there is **nothing suspiciously odd** with the data.
   
      <img src="Doc/check_TE.png" width="300" height="80"> <br/><br/>   
      <img src="Doc/check_fit.png" width="600" height="450"> 

 

# Documentation:
A description of the Class definitions and Methods used in this code is available in the [Documentation.md](Doc/Documentation.md) file inside the ```/Doc``` folder of this repository.



