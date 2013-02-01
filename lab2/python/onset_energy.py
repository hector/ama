# -*- coding: utf-8 -*-
from pylab import *
from scikits.audiolab import *  
from utils import *
from descriptors import *     

path = '../melodies/melody12.wav'

sndfile, x = read_sndfile(path) # read audio
fs = sndfile.samplerate # sampling frequency
x = normalize(x, 0.95) # normalize to 95%
#convolve(audio,[ 1, -1]) # low-pass filter #TODO: find a good way 

#==============================================================================
# WAVEFORM ENERGY
#==============================================================================
# e: power of the waveform 
#    - different methods proposed below (one per line), uncomment to change
M = window_bins(25, fs) # window for computing energy

# WAVEFORM ENVELOPE
e = avg_envelope(x, M)
#e = median_envelope(x, M)

# RMS
#e = rms(x, M)

# ENERGY
#e = avg_energy(x, M)
#e = median_energy(x, M)

#==============================================================================
# LOUDNESS
#==============================================================================
# Our hearing perception behaves logarithmically
log_e = dB(e, 1) # does not make sense to multiply the log here

#==============================================================================
# DERIVATIVE
#==============================================================================
# We want to detect changes in energy
N = window_bins(25, fs) # window for derivating
diff_e = mean_diff(log_e, N)
#diff_e = median_diff(log_e, N) # alternative

#==============================================================================
# DECIMATE
#==============================================================================
# A techinque for smoothing (we need to get rid of HF)
dec = 1
#mod_energy = decimate(mod_energy, trunc)

#==============================================================================
# FIND PEAKS
#==============================================================================

norm_e = normalize(diff_e, 1) # it is nicer to see it normalized
klocal = window_bins(50, fs) # number of samples to consider the local peaks
threshold = mean(abs(norm_e))
ploc = peaks(norm_e, klocal, threshold, 0) # onsets peak locations
ploc_off = peaks(norm_e * -1, klocal, threshold, 0) # offsets peak location

#==============================================================================
# DISCARD BY BPM COINCIDENCE (experimental and messy..)
#==============================================================================
bpm_on = True

def bpm_func(locs, th=0.5):
    bpm1 = locs[1:-1] - locs[:-2]
    bpm2 = abs(locs[1:-1] - locs[2:])
    bpm = bpm1 + bpm2
    bpm -= mean(bpm) # centrate on y=0
    bpm = normalize(bpm, 1) # normalize for nice visualization and thresholding
    bpm_locs = locs[1:-1]
    
    # discarded peak locs
    bpm_disc_locs = where(abs(bpm) > th)[0] 
    bpm_ok_locs = abs(bpm) <= th
    bpm_ok_locs = append(insert(bpm_ok_locs, 0, True), True)
    locs = locs[bpm_ok_locs] # delete discarded peaks
    return locs, bpm, bpm_locs, bpm_locs[bpm_disc_locs]
    
if bpm_on:    
    bpm_th = 0.85 
    ploc, bpm, bpm_locs, bpm_disc_locs = bpm_func(ploc, bpm_th)
    ploc_off, bpm_off, bpm_off_locs, bpm_off_disc_locs = bpm_func(ploc_off, bpm_th)     
 
#==============================================================================
# PLOTS 
#==============================================================================
y = norm_e
def plot_onsets(t, locs, color='r'):
    for loc in locs:
        axvline(t[loc], color=color)   

t = linspace(0, x.size/fs, x.size)    

figure()

subplot(2,1,1)
plot(t, x)
ylabel('amplitude')
title('melody 12')
ylim(-1.0,1.0)
plot_onsets(t, ploc*dec, 'r')
plot_onsets(t, ploc_off*dec, 'g')   
axhline(color='black') # y=0

subplot(2,1,2)
plot(t[:y.size*dec:dec], y)
xlabel('time (s)')
title('decision function')
ylim(-1.0,1.0)
plot(t[ploc*dec], y[ploc], 'o', color='r')
plot(t[ploc_off*dec], y[ploc_off], 'o', color='g')
plot_onsets(t, ploc*dec, 'r')
plot_onsets(t, ploc_off*dec, 'g')  
axhline(threshold, color='r', linestyle='--') # threshold line onsets
axhline(-threshold, color='g', linestyle='--') # threshold line offsets
axhline(color='black') # y=0

if bpm_on:
    plot(t[bpm_locs*dec], bpm, color='purple')
    plot(t[bpm_disc_locs*dec], y[bpm_disc_locs], 'o', color='purple')    
    plot_onsets(t, bpm_disc_locs, 'purple')
    
    plot(t[bpm_off_locs*dec], bpm_off, color='orange')
    plot(t[bpm_off_disc_locs*dec], y[bpm_off_disc_locs], 'o', color='orange')    
    plot_onsets(t, bpm_off_disc_locs, 'orange')    
    
    axhline(bpm_th, color='purple', linestyle='--')
    axhline(-bpm_th, color='purple', linestyle='--')    