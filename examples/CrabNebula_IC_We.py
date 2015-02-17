#!/usr/bin/env python
import numpy as np
import naima
import astropy.units as u
from astropy.io import ascii

## Read data

data=ascii.read('CrabNebula_HESS_2006_ipac.dat')

## Model definition

from naima.models import InverseCompton, ExponentialCutoffPowerLaw

def ElectronIC(pars,data):
    # Example of a model that is normalized though the total energy in electrons

    # Match parameters to ECPL properties, and give them the appropriate units
    We = 10**pars[0] * u.erg
    alpha = pars[1]
    e_cutoff = (10**pars[2])*u.TeV

    # Initialize instances of the particle distribution and radiative model
    ECPL = ExponentialCutoffPowerLaw(1/u.eV,10.*u.TeV, alpha, e_cutoff)
    IC = InverseCompton(ECPL,seed_photon_fields=['CMB'])
    IC.set_We(We,Eemin=1*u.TeV)

    # compute flux at the energies given in data['energy'], and convert to units
    # of flux data
    model = IC.flux(data,distance=2.0*u.kpc).to(data['flux'].unit)

    # Save this realization of the particle distribution function
    elec_energy = np.logspace(11,15,100) * u.eV
    nelec = ECPL(elec_energy)

    # The first array returned will be compared to the observed spectrum for
    # fitting. All subsequent objects will be stores in the sampler metadata
    # blobs.
    return model, (elec_energy,nelec)

## Prior definition

def lnprior(pars):
	"""
	Return probability of parameter values according to prior knowledge.
	Parameter limits should be done here through uniform prior ditributions
	"""

	logprob = naima.uniform_prior(pars[0],0.,np.inf) \
                + naima.uniform_prior(pars[1],-1,5)

	return logprob

if __name__=='__main__':

## Set initial parameters and labels

    p0=np.array((40,3.0,np.log10(30),))
    labels=['log10(We)','index','log10(cutoff)']

## Run sampler

    sampler,pos = naima.run_sampler(data_table=data, p0=p0, labels=labels, model=ElectronIC,
            prior=lnprior, nwalkers=32, nburn=100, nrun=20, threads=4, prefit=True)

## Save sampler
    from astropy.extern import six
    from six.moves import cPickle
    sampler.pool=None
    cPickle.dump(sampler,open('CrabNebula_IC_We_sampler.pickle','wb'))

## Diagnostic plots

    naima.save_diagnostic_plots('CrabNebula_IC_We',sampler,sed=True,last_step=False,
            blob_labels=['Spectrum', 'Electron energy distribution'])
    naima.save_results_table('CrabNebula_IC_We',sampler)


