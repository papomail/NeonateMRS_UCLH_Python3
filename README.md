# Neonate MRS UCLH (Python3)
#### The Department of Medical Physics and Biomedical Engineering at University College London Hospitals.
This repository contains the scripts used to process and produce automated reports of neonatal NMR spectra acquired at 3T MRI scanners at University College London Hospital.    

***Reports must be approved by a MRI Clinical Scientist @UCLH before being forwarded to the Neonatal Care Unit @UCLH***


### Requirements:
* Python =>3.7 (with sys, os, csv, numpy, PyPDF2, PathLib, FPDF & PyQt5 depencencies)
* Tarquin 4.x 
* 3_0T_basis_threonine_no_MM as *prior knowledge* for Tarquin
* MRS_Convert.py
* Spec_Module.py


## Who is it for:
This script is meant to be used by MRI Clinical Scientists.  
Its purpose is to assist in the processing of MRS data acquired @UCLH and to generate reports for the clinical team in a quick and robust manner. However, it does not exclude the need of MR expertise and knowledge of neonate MR spectroscopy for its correct use.  

***This script is NOT intended as an unsupervised data processing solution.***


## How to use it:
1) Run **MRS_Convert.py** script:
   - In a terminal open the folder contains the Neonate MRS scripts and type: 
      >```python MRS_Convert.py```
2) Select *input folder* (with DICOM data) and the *output folder* (where proccesd data will be saved):
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

 

## Documentation:
A description of the Class definitions and Methods used in this code is available in the [Documentation.md](Doc/Documentation.md) file inside the ```/Doc``` folder of this repository.



