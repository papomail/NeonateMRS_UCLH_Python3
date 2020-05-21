'''
UNITTEST: test_Spec_Module

Version 0.9
Modified 21/05/2020

Unitest for Spec_Module.py

Created on 10/04/020 @author: Patxi Torrealdea
'''



import unittest
import Spec_Module as sp
import numpy as np
from pathlib import Path
from matplotlib import pyplot as plt
import copy


class Test_Spec_Module(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        filename = str(Path.cwd() / "UnittestFiles/XX_0060")
        BaseDir = Path.cwd()
        dirpass = str(BaseDir.resolve())
        cls.output_figure = BaseDir / "UnittestFiles/unittest_fig.png"
        # print(f'cls.output_figure={cls.output_figure}')
        cls.mysp = sp.SpecObject(filename, dirpass)
        cls.chosen_frame = 3
        cls.excludeFrames = [0, 5, 15]
        cls.mysp.curframe = cls.chosen_frame

        return super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        plt.show(block=False)
        plt.savefig(cls.output_figure)
        print(f"\nResults figure saved in {cls.output_figure}")
        return super().tearDownClass()

    def test_phaseinc(self):
        curframe = self.mysp.curframe
        self.complex_init = self.mysp.curcomplex[curframe]

        zeros_array = np.zeros(self.complex_init.size, dtype="complex")

        self.mysp.phaseinc(0)
        complex_plus0 = self.mysp.curcomplex[curframe]

        self.mysp.phaseinc(360)
        self.complex_plus360 = self.mysp.curcomplex[curframe]

        self.mysp.phaseinc(5)
        self.mysp.phaseinc(-5)
        complex_5minus5 = self.mysp.curcomplex[curframe]

        self.mysp.phaseinc(-180)
        self.complex_minus180 = self.mysp.curcomplex[curframe]

        print("\nCheking test_phaseinc:")
        np.testing.assert_allclose(self.complex_init, complex_plus0)
        print(f"  Spectrum(a+0) = Spectrum(a) test: PASSED")
        np.testing.assert_allclose(self.complex_init, self.complex_plus360)
        print(f"  Spectrum(a+360) = Spectrum(a) test: PASSED")
        np.testing.assert_allclose(-self.complex_init, self.complex_minus180)
        print(f"  Spectrum(a+180) = -Spectrum(a) test PASSED")
        np.testing.assert_allclose(self.complex_init, complex_5minus5)
        print(f"  Spectrum(a+5) + Spectrum(a-5) = Spectrum(a) test: PASSED")
        should_be_false = np.allclose(self.complex_init, self.complex_minus180)
        self.assertFalse(should_be_false)
        print(f"  Spectrum(a+180) != Spectrum(a) test: PASSED\n")

        self.mysp.phaseinc(180)  # back to original phase
        self.plot_test_phaseinc()

    def test_Choinc(self):
        curframe = self.mysp.curframe
        ppa_init = self.mysp.peakposarr[curframe].copy()

        self.mysp.Choinc(0)
        ppa_0 = self.mysp.peakposarr[curframe].copy()

        self.mysp.Choinc(1)
        ppa_1 = self.mysp.peakposarr[curframe].copy()

        self.mysp.Choinc(-1)
        ppa_1minus1 = self.mysp.peakposarr[curframe].copy()

        print("\nCheking test_Choinc:")
        self.assertEqual(ppa_0[0], ppa_init[0])
        print(f"  Cho position + Choinc(0) = Cho position  test: PASSED")

        self.assertEqual(ppa_1[0], ppa_init[0] + 1)
        print(f"  Cho position + Choinc(1) = Cho position + 1  test: PASSED")

        self.assertEqual(ppa_1minus1[0], ppa_init[0])
        print(f"  Cho position + Choinc(1) + Choinc(-1) = Cho position  test: PASSED")

    def test_Crinc(self):
        curframe = self.mysp.curframe
        ppa_init = self.mysp.peakposarr[curframe].copy()

        self.mysp.Crinc(0)
        ppa_0 = self.mysp.peakposarr[curframe].copy()

        self.mysp.Crinc(1)
        ppa_1 = self.mysp.peakposarr[curframe].copy()

        self.mysp.Crinc(-1)
        ppa_1minus1 = self.mysp.peakposarr[curframe].copy()

        print("\nCheking test_Crinc:")
        self.assertEqual(ppa_0[1], ppa_init[1])
        print(f"  Cr position + Crinc(0) = Cr position  test: PASSED")

        self.assertEqual(ppa_1[1], ppa_init[1] + 1)
        print(f"  Cr position + Crinc(1) = Cr position + 1  test: PASSED")

        self.assertEqual(ppa_1minus1[1], ppa_init[1])
        print(f"  Cr position + Crinc(1) + Crinc(-1) = Cr position  test: PASSED")

    def test_addframes(self):
        complex_init = self.mysp.curcomplex[self.mysp.curframe]
        shift_peak_by = 200
        x = 1000

        mysp2 = copy.copy(self.mysp)
        nframes = len(mysp2.curcomplex)
        myinclude = [0 if ii in self.excludeFrames else 1 for ii in range(nframes)]
        mysp2.IncludeFrame = myinclude

        mysp2.curframe = self.chosen_frame
        KSpace_initial = self.mysp.Kspacewrite[mysp2.curframe]

        print("\nCheking test_addframes:")
        KSnew = mysp2.Kspacewrite[mysp2.curframe]
        self.assertAlmostEqual(KSpace_initial[x], KSnew[x])
        print(f"  KSpace1[x] = KSpace2[x]  test: PASSED")
        # print(f'mysp2.peakposarr={mysp2.peakposarr}')
        mysp2.Choinc(shift_peak_by)  # Update Cho peak
        # print(f'mysp2.peakposarr={mysp2.peakposarr}')

        KSnew = mysp2.Kspacewrite[mysp2.curframe]
        self.assertNotAlmostEqual(KSpace_initial[x], KSnew[x])
        print(f"  KSpace1[x] != KSpace2.Choinc(s)[x]  test: PASSED")
        complex_new = np.fft.fftshift(np.fft.fft(KSnew))

        # self.Kspacewrite[cnt] = np.fft.ifft(np.fft.fftshift(addcomplex))

        shiftindex = []
        med = []
        mysum = []
        for cnt in range(0, nframes):

            # try:
            #     ind = np.int(np.floor(   (mysp2.peakposarr[cnt][0] + mysp2.peakposarr[cnt][1])/2  ) )
            #     shiftindex.append(ind)
            # except:
            #     ind = 0
            #     shiftindex.append(ind)
            # if ind > 0:
            #     med.append(ind)
            ind = np.int(
                np.floor((mysp2.peakposarr[cnt][0] + mysp2.peakposarr[cnt][1]) / 2)
            )
            shiftindex.append(ind)
            med.append(ind)
            mysum.append(mysp2.Kspacewrite[cnt].sum())

        med_shift_index = np.floor(np.median(med))
        # print(f'med_shift_index={med_shift_index}')
        shift = int(med_shift_index - shiftindex[mysp2.curframe])
        # print(f'shift={shift}')
        # self.assertAlmostEqual(KSpace_initial[x],KSnew[x]*np.exp(1j*2*np.pi*shift*mytime)[x])
        self.assertAlmostEqual(complex_init[x], complex_new[x + shift])
        print(f"  Sp1[x] = Sp2.Choinc(s)[x+s/2]   test: PASSED")

        for ii, ks in enumerate(mysum):
            if ii in self.excludeFrames:
                self.assertEqual(0, ks)
            else:
                self.assertNotEqual(0, ks)
        print(f"  KSpace[includeFrame] != 0   test: PASSED")
        print(f"  KSpace[excludeFrame] = 0   test: PASSED\n")

    """
    PLOTS:
    """

    def plot_test_phaseinc(self):
        fig, (ax1, ax2) = plt.subplots(2, 1)

        ks_i = np.fft.ifft(np.fft.fftshift(self.complex_init))
        ks_360 = np.fft.ifft(np.fft.fftshift(self.complex_plus360))
        ks_180 = np.fft.ifft(np.fft.fftshift(self.complex_minus180))

        ax1.plot(ks_i.real)
        ax1.plot(ks_360.real)
        ax1.legend(["Initial", "+360$\degree$"])
        ax1.set_title("Should be equal")
        ax1.axis("off")

        ax2.plot(ks_i.real)
        ax2.plot(ks_180.real)
        ax2.legend(["Initial", "-180$\degree$"])
        ax2.set_title("Should be opposite")
        ax2.axis("off")

        plt.text(
            len(ks_i.real) * 0.8,
            max(ks_i.real) * -1.7,
            f"Frame: {self.mysp.curframe}",
            size=8,
        )
        plt.text(
            len(ks_i.real) * 0,
            max(ks_i.real) * -1.7,
            f"Testing method: phaseinc ",
            size=8,
        )

        plt.tight_layout()


"""
MAIN:
"""


def main():
    unittest.main(exit=True)


if __name__ == "__main__":
    main()
