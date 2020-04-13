# To review:
* test github:
 >   - push test OK
 >   - pull test OK  

* Apodisation not working. Why?  
  > Use acurcomplex instead of curcomplex? I tried... still not working.  
  > (302) >> addcomplex = np.roll(self.curcomplex[cnt], shift)  
  > (308) >> self.Spectrumauto.append(self.curcomplex[cnt])
  
* Why is the frequency *shift = medianshift-frameshift* ? Is that true? Check.  

* Currently unused code:  

>  - **writejmruidata2()** method (works but the output file is unused; we use Tarquin)
  
 >   - **writejmruidata2orig()** method (works but the output file is unused, we use Tarquin)
  
* Check in **__ init __()**:

      Spectrumauto: Data array to store the corrected non-apodised spectrum.  (Is it used?)
 
      PatientName: Patient name extracted from the DICOM header. (Currently not unused).
    
      StudyDate:  Study date extracted from the DICOM header. (Currently not unused).
    
      StudyTime:  Study time extracted from the DICOM header. (Currently not unused).
    
      SeriesDate: Series date extracted from the DICOM header. (Currently not unused).
    
      SeriesTime: Series time extracted from the DICOM header. (Currently not unused).
      
      ...

  Review condition: *if [0x5600,0x0020] in self.ds:*.  Check what parameter we do actually use and simplify without condition statement. 
  
* Check in **autophase()**:

    >FinalKspaceauto: Data array to store the final corrected k-space as the sum of frames with IncludeFrame flag value 1. *(Redefined in **addframes()**. Unused here)*

    >FinalSpectrumauto:  Data array to store the final corrected spectrum as the sum of frames with IncludeFrame flag value 1. *(Redefined in **addframes()**. Unused here)*
     
    >Spectrumauto: Data array to store the corrected non-apodised spectrum.  (Not used)

    >Spectrumautoadop: Data array to store the corrected apodised spectrum. (Not used)
    
    >shiftindex: *(Redefined in **addframes()**. Unused here)*
    
   > med:  *(Redefined in **addframes()**. Unused here)*



* Left and right markers don't automatically get updated when using  **phasedialog()**. Calling **plotprocspec()** from **Phasereg()** does the trick.  
> add 'self.plotprocspec()' to **Phasereg()**


* Unused parameter PlotType in **plotorigspec()** and **plotprocspec()**


* Unused method **plotfit(self)** in **Maingui(QtGui.QMainWindow)** class.



#
## Testing colour schemes:
```diff
- text in red
+ text in green
! text in orange
# text in gray
```
