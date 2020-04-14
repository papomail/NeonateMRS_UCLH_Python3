import unittest
import Spec_Module as sp
import numpy as np
from pathlib import Path
from matplotlib import pyplot as plt
class Test_Spec_Module(unittest.TestCase):
    


    @classmethod
    def setUpClass(self):
        filename='/Users/papo/Sync/myDocker/DICOMMRS/XX_0060'
        HOME_DIR=Path.home()
        dirpass=str(HOME_DIR.resolve())
        self.mysp=sp.SpecObject(filename,dirpass)
        print('\nRun setUpClass')
        return super().setUpClass()

    # def setUp(self):
    #     filename='/Users/papo/Sync/myDocker/DICOMMRS/XX_0060'
    #     HOME_DIR=Path.home()
    #     self.dirpass=str(HOME_DIR.resolve())
    #     self.mysp=sp.SpecObject(filename,dirpass)
    #     return super().setUp()




    def test_phaseinc(self):
        

        complex_init=self.mysp.curcomplex[self.mysp.curframe]
        zeros_array=np.zeros(complex_init.size,dtype='complex')

        self.mysp.phaseinc(0)
        complex_plus0=self.mysp.curcomplex[self.mysp.curframe]

        self.mysp.phaseinc(360)
        complex_plus360=self.mysp.curcomplex[self.mysp.curframe]

        self.mysp.phaseinc(5)
        self.mysp.phaseinc(-5)
        complex_5minus5=self.mysp.curcomplex[self.mysp.curframe]

        self.mysp.phaseinc(-180)
        complex_minus180=self.mysp.curcomplex[self.mysp.curframe]

        print('\nCheking test_phaseinc:')
        print(f'  mysp= {self.mysp}')
        print(f'  curframe= {self.mysp.curframe}\n')

        np.testing.assert_allclose(complex_init,complex_plus0)
        print(f'  Spectrum(a+0) = Spectrum(a) tested.')

        np.testing.assert_allclose(complex_init,complex_plus360)
        print(f'  Spectrum(a+360) = Spectrum(a) tested.')

        np.testing.assert_allclose(-complex_init,complex_minus180)
        print(f'  Spectrum(a+180) = -Spectrum(a) tested.')

        np.testing.assert_allclose(complex_init,complex_5minus5)
        print(f'  Spectrum(a+5) + Spectrum(a-5) = Spectrum(a) tested.')

        

        #plot
        # c=[a+b for a,b in zip(complex_init,complex_minus180)]
        # fig,ax=plt.subplots()
        # ax.plot(np.real(c))
        # plt.show()

if __name__ == "__main__":
    unittest.main()        

 