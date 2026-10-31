"""Single isolated Gaussian peak analysis. No material assignment is inferred."""
import argparse
import json
from pathlib import Path
import numpy as np
from scipy.optimize import curve_fit

PARAMETERS = ['amplitude', 'center_eV', 'sigma_eV', 'baseline', 'slope_per_eV']
FWHM_FACTOR = 2 * np.sqrt(2 * np.log(2))

def model(x, amplitude, center, sigma, baseline, slope):
    return amplitude * np.exp(-0.5 * ((x - center) / sigma)**2) + baseline + slope * (x - np.mean(x))

def validate(x, y):
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if x.ndim != 1 or y.shape != x.shape or len(x) < 12:
        raise ValueError('Supply at least 12 paired one-dimensional samples.')
    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
        raise ValueError('Samples must be finite.')
    order = np.argsort(x)
    x, y = x[order], y[order]
    if np.any(np.diff(x) <= 0) or np.ptp(y) == 0:
        raise ValueError('Energy values must be unique; intensity must vary.')
    return x, y

def fit(x, y):
    x, y = validate(x, y)
    span = np.ptp(x)
    edge = max(2, len(x)//10)
    idx = np.r_[0:edge, len(x)-edge:len(x)]
    slope, base = np.polyfit(x[idx] - x.mean(), y[idx], 1)
    signal = y - base - slope*(x-x.mean())
    p0 = [max(signal.max(), 1e-12), x[np.argmax(signal)], span/12, base, slope]
    lower = [0, x.min(), np.min(np.diff(x))/4, -np.inf, -np.inf]
    upper = [np.inf, x.max(), span/2, np.inf, np.inf]
    params, cov = curve_fit(model, x, y, p0=p0, bounds=(lower, upper), maxfev=20000)
    residual = y - model(x, *params)
    errors = np.sqrt(np.diag(cov))
    warnings = []
    if not np.all(np.isfinite(errors)):
        warnings.append('Covariance uncertainty could not be estimated reliably.')
    if params[1]-3*params[2] < x.min() or params[1]+3*params[2] > x.max():
        warnings.append('Peak tails extend beyond the fit window; baseline and width may be unreliable.')
    for i in range(3):
        if np.isclose(params[i], lower[i], rtol=1e-4, atol=1e-10) or np.isclose(params[i], upper[i], rtol=1e-4, atol=1e-10):
            warnings.append(f'{PARAMETERS[i]} is near a fit bound; uncertainty is not reliable.')
    result = {'model': 'Gaussian + linear baseline', 'samples': len(x),
              'parameters': dict(zip(PARAMETERS, params.tolist())),
              'standard_errors': {k: float(v) if np.isfinite(v) else None for k,v in zip(PARAMETERS, errors)},
              'fwhm_meV': float(FWHM_FACTOR*params[2]*1000),
              'fwhm_standard_error_meV': float(FWHM_FACTOR*errors[2]*1000) if np.isfinite(errors[2]) else None,
              'residual_rmse': float(np.sqrt(np.mean(residual**2))), 'warnings': warnings,
              'uncertainty_note': 'Local covariance standard errors, conditional on this model and independent, constant-variance noise; not calibration or systematic uncertainty.'}
    return x, y, params, result

def demo(path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    x = np.linspace(1.75, 1.95, 401)
    truth = [1000., 1.85, .012, 80., 120.]
    y = model(x, *truth) + np.random.default_rng(42).normal(0, 15, x.size)
    np.savetxt(path/'synthetic_spectrum.csv', np.c_[x,y], delimiter=',', header='energy_eV,intensity', comments='')
    (path/'synthetic_truth.json').write_text(json.dumps({'provenance':'SIMULATED; not experimental data or a specific material', 'seed':42, 'noise_std':15, 'parameters':dict(zip(PARAMETERS,truth))}, indent=2)+'\n')

def analyze(source, out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    data = np.genfromtxt(source, delimiter=',', names=True)
    if not data.dtype.names or not {'energy_eV','intensity'}.issubset(data.dtype.names):
        raise ValueError('CSV must contain energy_eV and intensity columns.')
    x,y,p,r = fit(data['energy_eV'], data['intensity'])
    r['input_file'] = Path(source).name
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    (out/'fit_summary.json').write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
    np.savetxt(out/'fit_curve.csv', np.c_[x,y,model(x,*p),y-model(x,*p)], delimiter=',', header='energy_eV,intensity,fit,residual',comments='')
    fig,(ax,res) = plt.subplots(2,1,figsize=(8,6),sharex=True,gridspec_kw={'height_ratios':[3,1]},layout='constrained')
    ax.plot(x,y,'.',color='#90a4ae',markersize=3,label='Input spectrum')
    ax.plot(x,model(x,*p),color='#00796b',lw=2,label='Gaussian + baseline')
    ax.set(ylabel='Intensity (a.u.)', title=Path(source).stem.replace('_',' ').title())
    ax.legend(frameon=False)
    ax.text(.03,.94,f'Center: {p[1]:.5f} eV\nFWHM: {r["fwhm_meV"]:.2f} meV', transform=ax.transAxes,va='top')
    res.axhline(0,color='#607d8b',lw=1)
    res.plot(x,y-model(x,*p),color='#546e7a',lw=.8)
    res.set(xlabel='Photon energy (eV)',ylabel='Residual')
    for a in (ax,res):
        a.spines[['top','right']].set_visible(False)
    fig.savefig(out/'spectrum_fit.png',dpi=200)
    fig.savefig(out/'spectrum_fit.svg')
    plt.close(fig)
    return r

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command',required=True)
    d = sub.add_parser('demo'); d.add_argument('--out',default='data')
    a = sub.add_parser('fit'); a.add_argument('csv'); a.add_argument('--out',default='results')
    args = parser.parse_args()
    if args.command == 'demo': demo(args.out)
    else: print(json.dumps(analyze(args.csv,args.out),indent=2))
