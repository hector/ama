# -*- coding: utf-8 -*-
from pylab import *
import scikits.audiolab as alab
import types
NumberTypes = (types.IntType, types.LongType, types.FloatType, types.ComplexType)

def _lcall(function_name):
    """Returns the local function with function_name"""
    return globals()[function_name]

def read_sndfile(path):
    """Read any audio file
    Returns (snd_file, first_channel_data_array)
    """
    sound_file = alab.Sndfile(path)
    data = sound_file.read_frames(sound_file.nframes)
    if sound_file.channels > 1: data = data[1] # get only first channel
    return sound_file, data 
    
def dB(vector, mul=10):
    """Transform vector to decibels avoinding -Inf results"""
    vector[vector==0] = spacing(1) # avoid -Inf results with spacing()
    return mul*log10(vector) 
    
def window_bins(miliseconds, sample_rate):
    """Returns the size in bins for a window of the desired milliseconds"""
    return sample_rate * miliseconds // 1000  
    
def normalize(x, max_value=1, center=0):
    """Normalize +x+ to +max_value+ centering the mean to +center+
    To no center set +center+ to None"""
    maximum = float(abs(x[nanargmax(abs(x))]))
    assert maximum != 0 and maximum != nan and maximum != Inf and maximum != -Inf, "Invalid value for normalizing: max = %s" % maximum
    if center != None: x = x - (mean(x) + center)
    return x * max_value / maximum 
    
def my_diff(x):
    """I made this differentation function just to preserve x.size"""
    return append(diff(x), 0)    
    
def _rms(x):
    """Root mean square"""
    assert x.ndim == 1, "Input must be one-dimensional." 
    return sqrt(mean(x**2))  
    
def decimate(x,k=2):
    """Return a decimated version of x, i.e only one sample very k"""
    return x[::k]    
    
#==============================================================================
# FILTERS    
#==============================================================================
    
def one_window_filter(x, k=11, op='mean'):
    """"Apply a length-k +op+ filter to a 1D array x.
    This filters uses a single moving window and will
    apply to it the +op+ function
    """
    assert k % 2 == 1, "Filter length must be odd."
    assert x.ndim == 1, "Input must be one-dimensional."    
    
    y = zeros_like(x)
    M = k // 2 # half of the window
    for i in range(x.size):
        lp = max(0,i-M) # left pointer of the window
        rp = min(x.size,i+M) # right pointer of the window        
        y[i] = _lcall(op)(x[lp:rp]) 
    return y       

def mean_filter(x, k=11):
    """"Apply a length-k mean filter to a 1D array x."""
    return one_window_filter(x, k, 'mean')
    
def median_filter(x, k=11):
    """"Apply a length-k median filter to a 1D array x."""
    return one_window_filter(x, k, 'median')
    
def rms_filter(x, k=11):
    """"Apply a length-k RMS filter to a 1D array x."""
    return one_window_filter(x, k, '_rms')    
    
#==============================================================================
# DIFFERENTIATION    
#==============================================================================
    
def wdiff(x, k=10, op='mean'):
    """Windowed differenciation. Use to windows (left and right of
    the iterator) with +k+ length to compute the difference. In each 
    window the function +op+ will be applied.
    """
    assert x.ndim == 1, "Input must be one-dimensional." 
    
    y = zeros_like(x)            
    for i in range(1, x.size-1):
        lp = max(0, i-k) # left pointer of the window
        rp = min(x.size, i+k+1) # right pointer of the window 
        lw = _lcall(op)(x[lp:i]) # left window
        rw = _lcall(op)(x[i+1:rp]) # right window
        y[i] = rw - lw
    return y

def mean_diff(x, k=10):
    """Apply the difference of the mean of two moving windows"""
    return wdiff(x, k, 'mean')    
    
def median_diff(x, k=10):
    """Apply the difference of the median of two moving windows"""
    return wdiff(x, k, 'median') 
    
def medfilt (x, k): # https://gist.github.com/3535131
    """Apply a length-k median filter to a 1D array x.
    Boundaries are extended by repeating endpoints.
    """
    assert k % 2 == 1, "Median filter length must be odd."
    assert x.ndim == 1, "Input must be one-dimensional."
    k2 = (k - 1) // 2
    y = zeros ((len (x), k), dtype=x.dtype)
    y[:,k2] = x
    for i in range (k2):
        j = k2 - i
        y[j:,i] = x[:-j]
        y[:j,i] = x[0]
        y[:-j,-(i+1)] = x[j:]
        y[-j:,-(i+1)] = x[-1]
    return median (y, axis=1)    
    
def rms_diff(x, k=10):
    """Apply the difference of the RMS of two moving windows"""
    return wdiff(x, k, '_rms') 
  
#==============================================================================
# PEAKS
#==============================================================================
  
def peaks(x, k=1, th=None, append_with=None):
    """Returns local maximums location in 1D vector
    If the are various equal maximums it chooses the one more in the left
    If threshold +th+ is specified only returns maximums above it
    k: is the number of samples to consider the local maximum (#neighbours compared)
    append_with: number to use to append to the extremes. By default the extremes of x
      are not considered as maximums by definition. If append_with is set, they are.
    """    
    if isinstance(append_with, NumberTypes): x = append(zeros(k), append(x, zeros(k)))
    candidates = x[k:-k] # extremes cannot be maximas by definition
    peaks = empty_like(candidates);
    peaks[:] = True
    
    for i in arange(k):
        gtL = greater_equal(candidates, x[i : candidates.size+i]) # greater than immediate left values
        gtR = greater(candidates, x[x.size-candidates.size-i : x.size-i]) # greater than immedate right values
        peaks = logical_and(peaks, gtL);
        peaks = logical_and(peaks, gtR);
        
    if th:
        above_th = candidates > th # candiadtes above threshold
        peaks = logical_and(peaks, above_th)
    
    locs = where(peaks)[0]
    if not isinstance(append_with, NumberTypes): locs += k # +k offset because of discarded extremes      :
    return locs