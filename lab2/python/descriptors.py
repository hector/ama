# -*- coding: utf-8 -*-
from pylab import *
from scikits.audiolab import * 
from utils import *

#==============================================================================
# ENERGY
#==============================================================================

def inst_energy(x):
    """Compute instantaneous energy (audio**2)"""
    return x**2

def avg_energy(x, window_size=11):
    """Calculate the energy using an average moving window for smoothing"""
    return mean_filter(inst_energy(x), window_size)
    
def median_energy(x, window_size=11):
    """Calculate the energy using a median moving window for smoothing"""
    return median_filter(inst_energy(x), window_size)
    
def avg_denergy(x, window_size=11):
    """Calculate the energy using the difference of the mean 
    of two moving windows for smoothing"""
    return mean_diff(inst_energy(x), window_size)    
    
def median_denergy(x, window_size=11):
    """Calculate the energy using the difference of the mean 
    of two moving windows for smoothing"""
    return median_diff(inst_energy(x), window_size)  

#==============================================================================
# WAVEFORM ENVELOPE
#==============================================================================

def avg_envelope(x, window_size=11):
    """Calculate the waveform envelope using an average moving window for smoothing"""    
    return mean_filter(abs(x), window_size)
    
def median_envelope(x, window_size=11):
    """Calculate the waveform envelope using a median moving window for smoothing"""    
    return mean_filter(abs(x), window_size)
    
def avg_denvelope(x, window_size=11):
    """Calculate the waveform envelope using the difference of the mean 
    of two moving windows for smoothing"""
    return mean_diff(abs(x), window_size)    
    
def median_denvelope(x, window_size=11):
    """Calculate the waveform envelope using the difference of the mean 
    of two moving windows for smoothing"""
    return median_diff(abs(x), window_size)      

#==============================================================================
# ROOT MEAN SQUARE    
#==============================================================================
        
def rms(x, window_size=11):
    """Calculate the RMS using a moving window"""    
    return rms_filter(x, window_size)
    
def drms(x, window_size=11):
    """Calculate the RMS using the difference of of two moving windows"""
    return rms_diff(x, window_size)
