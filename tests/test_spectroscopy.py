import unittest
import numpy as np
from spectroscopy import fit, model, FWHM_FACTOR

class SpectrumTests(unittest.TestCase):
    def test_noisy_peak_recovery(self):
        x = np.linspace(1.75,1.95,401)
        y = model(x,1000,1.85,.012,80,120) + np.random.default_rng(42).normal(0,15,len(x))
        _,_,p,r = fit(x,y)
        self.assertAlmostEqual(p[1],1.85,delta=.0002)
        self.assertAlmostEqual(r['fwhm_meV'],FWHM_FACTOR*12,delta=.5)
    def test_reversed_input(self):
        x = np.linspace(1.75,1.95,401)
        y = model(x,1000,1.85,.012,80,120)
        _,_,p,_ = fit(x[::-1],y[::-1])
        np.testing.assert_allclose(p,[1000,1.85,.012,80,120],rtol=1e-5)
    def test_bad_inputs(self):
        for x,y in [(np.arange(10),np.arange(10)),(np.ones(20),np.arange(20)),(np.arange(20),np.ones(20)),(np.arange(20),np.full(20,np.nan))]:
            with self.assertRaises(ValueError): fit(x,y)
    def test_truncated_peak_warns(self):
        x=np.linspace(1.84,1.92,101)
        _,_,_,r=fit(x,model(x,1000,1.85,.012,80,120))
        self.assertTrue(r['warnings'])

if __name__ == '__main__': unittest.main()
