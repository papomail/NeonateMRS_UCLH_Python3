import unittest
import Spec_Module as sp
import numpy as np
from pathlib import Path
from matplotlib import pyplot as plt
import sys




class Test_Spec_Module(unittest.TestCase):
    


    @classmethod
    def setUpClass(cls):
        filename='/Users/papo/Sync/myDocker/DICOMMRS/XX_0060'
        HOME_DIR=Path.home()
        dirpass=str(HOME_DIR.resolve())
        cls.output_figure=HOME_DIR/'Desktop/unittest_fig.png'
        cls.mysp=sp.SpecObject(filename,dirpass)
        cls.mysp.curframe=6
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        plt.show(block=False)  
        plt.savefig(cls.output_figure)
        print(f'\nResults figure saved in {cls.output_figure}')
        return super().tearDownClass()
    




    def test_phaseinc(self):
        curframe=self.mysp.curframe

        self.complex_init=self.mysp.curcomplex[curframe]
        zeros_array=np.zeros(self.complex_init.size,dtype='complex')

        self.mysp.phaseinc(0)
        complex_plus0=self.mysp.curcomplex[curframe]

        self.mysp.phaseinc(360)
        self.complex_plus360=self.mysp.curcomplex[curframe]

        self.mysp.phaseinc(5)
        self.mysp.phaseinc(-5)
        complex_5minus5=self.mysp.curcomplex[curframe]

        self.mysp.phaseinc(-180)
        self.complex_minus180=self.mysp.curcomplex[curframe]

        print('\nCheking test_phaseinc:')  
        np.testing.assert_allclose(self.complex_init,complex_plus0)
        print(f'  Spectrum(a+0) = Spectrum(a) test: PASSED')
        np.testing.assert_allclose(self.complex_init,self.complex_plus360)
        print(f'  Spectrum(a+360) = Spectrum(a) test: PASSED')
        np.testing.assert_allclose(-self.complex_init,self.complex_minus180)
        print(f'  Spectrum(a+180) = -Spectrum(a) test PASSED')
        np.testing.assert_allclose(self.complex_init,complex_5minus5)
        print(f'  Spectrum(a+5) + Spectrum(a-5) = Spectrum(a) test: PASSED')
        should_be_false=np.allclose(self.complex_init, self.complex_minus180)
        self.assertFalse(should_be_false)
        print(f'  Spectrum(a+180) != Spectrum(a) test: PASSED\n')

        self.plot_test_phaseinc()
        


        

    def test_Choinc(self):
        curframe=self.mysp.curframe
        ppa_init = self.mysp.peakposarr[curframe].copy()
        
        self.mysp.Choinc(0)
        ppa_0 = self.mysp.peakposarr[curframe].copy()

        self.mysp.Choinc(1)
        ppa_1 = self.mysp.peakposarr[curframe].copy()

        self.mysp.Choinc(-1)
        ppa_1minus1 = self.mysp.peakposarr[curframe].copy()

        print('\nCheking test_Choinc:')  
        self.assertEqual(ppa_0[0],ppa_init[0])
        print(f'  Cho position + Choinc(0) = Cho position  test: PASSED')

        self.assertEqual(ppa_1[0],ppa_init[0]+1)
        print(f'  Cho position + Choinc(1) = Cho position + 1  test: PASSED')

        self.assertEqual(ppa_1minus1[0],ppa_init[0])
        print(f'  Cho position + Choinc(1) + Choinc(-1) = Cho position  test: PASSED')

        
    
    def test_Crinc(self):
        curframe=self.mysp.curframe
        ppa_init = self.mysp.peakposarr[curframe].copy()
        
        self.mysp.Crinc(0)
        ppa_0 = self.mysp.peakposarr[curframe].copy()

        self.mysp.Crinc(1)
        ppa_1 = self.mysp.peakposarr[curframe].copy()

        self.mysp.Crinc(-1)
        ppa_1minus1 = self.mysp.peakposarr[curframe].copy()

        print('\nCheking test_Crinc:')  
        self.assertEqual(ppa_0[1],ppa_init[1])
        print(f'  Cr position + Crinc(0) = Cr position  test: PASSED')

        self.assertEqual(ppa_1[1],ppa_init[1]+1)
        print(f'  Cr position + Crinc(1) = Cr position + 1  test: PASSED')

        self.assertEqual(ppa_1minus1[1],ppa_init[1])
        print(f'  Cr position + Crinc(1) + Crinc(-1) = Cr position  test: PASSED')


   
    def plot_test_phaseinc(self):
        fig,(ax1,ax2)=plt.subplots(2,1)

        ks_i=np.fft.ifft(np.fft.fftshift(self.complex_init))
        ks_360=np.fft.ifft(np.fft.fftshift(self.complex_plus360))
        ks_180=np.fft.ifft(np.fft.fftshift(self.complex_minus180))

        ax1.plot(ks_i.real)
        ax1.plot(ks_360.real)
        ax1.legend(['Initial','+360$\degree$'])
        ax1.set_title('Should be equal')
        ax1.axis('off')

        ax2.plot(ks_i.real)
        ax2.plot(ks_180.real)
        ax2.legend(['Initial','-180$\degree$'])
        ax2.set_title('Should be opposite')
        ax2.axis('off')

        plt.text(len(ks_i.real)*0.8, max(ks_i.real)*-1.7, f'Frame: {self.mysp.curframe}',size=8)
        plt.text(len(ks_i.real)*0, max(ks_i.real)*-1.7, f'Testing method: phaseinc ',size=8)

        plt.tight_layout()



def main():   
    unittest.main(exit=True)


if __name__ == "__main__":
    main()
    

 