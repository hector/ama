#!/usr/bin/python
#==============================================================================
# Note segmentation based on fundamental frequency
#==============================================================================

import os
from distutils.dir_util import mkpath
import csv
from numpy import *
from matplotlib.pyplot import *
from utils import *

def find_peaks(vector,th):
   peaks = []
   (lx,ly) = vector.shape
   for i in range(1, lx-1):
       if(vector[i,1] > vector[i-1,1] and vector[i,1] > vector[i+1,1]):
           if( vector[i,1] > th):
               peaks.append(i)
   return array(peaks)
   
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

#==============================================================================
# Compute f0 from Aubio Vamp via Sonic-Annotator
#==============================================================================
mkpath("csv") # create dir for ouput. this does not fail if dir already exists
os.system("rm csv/*vamp_vamp-aubio_aubiopitch_frequency.csv") # Remove if csv's already exist

# Melody 4
#os.system("/usr/local/bin/sonic-annotator -s vamp:vamp-aubio:aubiopitch:frequency > aubiopitch_melody4.n3") # create transform file
os.system("/usr/local/bin/sonic-annotator -t aubiopitch_melody4.n3 ../melodies/melody4.wav -w csv --csv-basedir csv") # extract features for melody4
f0_melody = genfromtxt('csv/melody4_vamp_vamp-aubio_aubiopitch_frequency.csv',delimiter=',') #from csv to array

# Melody 19
##os.system("/usr/local/bin/sonic-annotator -s vamp:vamp-aubio:aubiopitch:frequency > aubiopitch_melody19.n3") # create transform file
#os.system("/usr/local/bin/sonic-annotator -t aubiopitch_melody4.n3 ../melodies/melody19.wav -w csv --csv-basedir csv") # extract features for melody4
#f0_melody = genfromtxt('csv/melody19_vamp_vamp-aubio_aubiopitch_frequency.csv',delimiter=',') #from csv to array

#==============================================================================
# Convert from Hertz to Cents
#==============================================================================
fbase = 440
f0_melody[:,1] = 1200*log2(f0_melody[:,1]/fbase) 

#==============================================================================
# Smooth the output of the f0 estimation
#==============================================================================
f0_melody_smooth = zeros_like(f0_melody) 
f0_melody_smooth[:,1]= medfilt(f0_melody[:,1], 15) # for melody 4
#f0_melody_smooth[:,1]= medfilt(f0_melody[:,1], 2) # for melody 19
f0_melody_smooth[:,0]= f0_melody[:,0]

#==============================================================================
# f0 Derivate
#==============================================================================
(a,b) = f0_melody_smooth.shape # initialize stuff
f0diff_melody = zeros((a-1,b))

f0diff_melody[:,1] =  diff(f0_melody_smooth[:,1]).conj().transpose()
f0diff_melody[:,0] = f0_melody_smooth[:-1,0] 

#==============================================================================
# Peak detection
#==============================================================================
th = 3 # Threshold for Melody4
#th = 3 # Threshold for Melody19

f0diff_melody = absolute(f0diff_melody)
peaks = find_peaks(f0diff_melody,th)
mags = f0_melody_smooth[peaks,1]
mags2 = f0diff_melody[peaks,1]

#==============================================================================
# Plotting results
#==============================================================================
figure(1)
subplot(2,1,1)
plot(f0_melody_smooth[:,0],f0_melody_smooth[:,1])
ylabel('f0 (cents)')
xlabel('Time (s)')
title('f0 estimation (Smoothed)')
hold(True)
plot(f0_melody_smooth[peaks,0],mags,'o')

subplot(2,1,2)
plot(f0diff_melody[:,0],f0diff_melody[:,1])
#ylabel('f0 (cents)')
xlabel('Time (s)')
title('f0 derivate')
hold(True)
plot(f0diff_melody[peaks,0],mags2,'o')