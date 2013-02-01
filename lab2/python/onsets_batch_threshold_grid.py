# -*- coding: utf-8 -*-
from pylab import *
import os
from distutils.dir_util import mkpath
import csv
from utils import *
from descriptors import *   


#filename = 'melody23'
filenames = [4,19,12,23,18]    
th = {'melody4': 0.05,'melody19': 0.3,'melody12': 0.48,'melody23': 0.535,'melody18': 0.6}
mx =  {'melody4': 1,'melody19': 0.5,'melody12': 0.5,'melody23': 0.5,'melody18': 0.4}
fmeasures = {}
precisions = {}
recalls = {}

for k in filenames:
    filename = 'melody%s' % k
    path = '../melodies/%s.wav' % filename
    threshold = th[filename]
    mixcoef = mx[filename] 
    fmeasures[filename] = {}
    precisions[filename] = {}
    recalls[filename] = {}
    
    for th_mul in arange(0.9, 1.3, 0.05):

        # mixcoef range [0:1] // 0.5 Balanced / O -> Only energy function / 1-> Only f0 function
        
        #==============================================================================
        #==============================================================================
        # # ONSETS BY FREQUENCY
        #==============================================================================
        #==============================================================================
        
        #==============================================================================
        # Compute f0 from Aubio Vamp via Sonic-Annotator
        #==============================================================================
        mkpath("csv") # create dir for ouput. this does not fail if dir already exists
        os.system("rm csv/%s_vamp_vamp-aubio_aubiopitch_frequency.csv" % filename) # Remove if csv's already exist
        #os.system("/usr/local/bin/sonic-annotator -s vamp:vamp-aubio:aubiopitch:frequency > aubiopitch_%s.n3" % filename) # create configuration file
        
        transfile = "aubiopitch_%s.n3" % filename
        # extract hop size from transform file
        with open(transfile) as f: lines = f.readlines()
        for l in lines:
            if "step_size" in l: 
                hop = int(l[l.find('"')+1:l.find('"', l.find('"')+1)]) # find number between quotation marks
                break
        
        os.system("/usr/local/bin/sonic-annotator -t %s %s -w csv --csv-basedir csv" % (transfile, path)) # extract features for melody4
        f0_melody = genfromtxt('csv/%s_vamp_vamp-aubio_aubiopitch_frequency.csv' % filename, delimiter=',') #from csv to array
        
        #==============================================================================
        # Convert from Hertz to Cents
        #==============================================================================
        fbase = 440
        f0_melody[:,1] = 1200*log2(f0_melody[:,1]/fbase) 
        
        #==============================================================================
        # Smooth the output of the f0 estimation
        #==============================================================================
        f0_melody_smooth = medfilt(f0_melody[:,1], 15)
        
        #==============================================================================
        # f0 Derivate
        #==============================================================================
        
        f0diff_melody = diff(f0_melody_smooth)#.conj().transpose()
        f0diff_melody = append(f0diff_melody, 0) # append 0 to preserve size
        
        f0diff_melody = abs(f0diff_melody)
        norm_f0 = normalize(f0diff_melody, center = None)
        
        #==============================================================================
        #==============================================================================
        # # ONSETS BY ENERGY
        #==============================================================================
        #==============================================================================
        
        sndfile, x = read_sndfile(path) # read audio
        fs = float(sndfile.samplerate) # sampling frequency
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
        diff_e = diff_e + abs(diff_e.min()) # move lowest point to zero
        norm_e = normalize(diff_e, 1, None) # normalize before mixing with frequency func
        
        #==============================================================================
        #==============================================================================
        # # ONSETS DETECTION
        #==============================================================================
        #==============================================================================
        
        #==============================================================================
        # MIX DECISION FUNCTIONS
        #==============================================================================
        # Interpolate linearly f0 before mixing to match norm_e size
        # We interpolate always with back points in a hop size distance (so unvoiced frames remain = 0)
        f0_samples = (f0_melody[:,0] * fs).round() 
        norm_f0_interp = zeros_like(norm_e)
        for i, sample in enumerate(f0_samples):
            if sample == 0: next() # jump first sample if its zero (we are interpolating with back points) 
            norm_f0_interp[sample-hop:sample] = linspace(norm_f0_interp[sample-hop-1], norm_f0[i], hop)
        final_interp = norm_f0_interp[f0_samples[-1]:f0_samples[-1]+hop]    
        final_interp = linspace(norm_f0_interp[-1], 0, final_interp.size)
        
        decision0 = mixcoef*norm_f0_interp + (1-mixcoef)*norm_e # mixing of decision functions
        
        decision = mean_filter(decision0, M)
        decision = normalize(decision, 1, None)
        
        #==============================================================================
        # FIND PEAKS
        #==============================================================================
        threshold = mean(decision) * th_mul
        klocal = window_bins(50, fs) # number of samples to consider the local peaks
        ploc = peaks(decision, klocal, threshold, 0) # onsets peak locations
        
        #==============================================================================
        # F-MEASURE
        #==============================================================================
        
        # Read ground truth from txt file
        with open('../markers/%s.txt' % filename) as f:
            lines = f.readlines()[1:-2]
        
        onsets_gt = empty(size(lines)) # initialize onsets ground truth
        i = 0
        for l in lines: 
            time = l.split()[-1].split(':') # format: [hours, mins, secs]
            onsets_gt[i] = float(time[2]) + (float(time[1]) + float(time[0])*60)*60
            i +=1
        
        onsets = ploc / fs # extract onsets time from location
        tolerance = 0.05 # onset tolerance in seconds
        
        cd = 0. # correct detection
        fn = 0. # false negative
        fp = 0. # false positive
        for gt in onsets_gt:
            if any(logical_and(onsets >= gt-tolerance, onsets <= gt+tolerance)): cd += 1
            else: fn += 1
        fp = onsets.size - cd
        if fp < 0: fp = 0 
        
        precision = cd / (cd + fp)
        recall = cd / (cd + fn)
        fmeasure = 2*precision*recall / (precision+recall) 
    
        precisions[filename][th_mul] = precision
        recalls[filename][th_mul] = recall
        fmeasures[filename][th_mul] = fmeasure
        
        print "%s with th_mul=%s done!" % (filename, th_mul)        
        
        #==============================================================================
        # PLOTS
        #==============================================================================
        #def plot_onsets(t, locs, color='r'):
            #for loc in locs:
                #axvline(t[loc], color=color) 
        #
        #def plot_gt(times, color='g'):
            #"Plot ground truth onsets"
            #for t in times:
                #axvline(t, color=color, linestyle='--')        
                #
        #t = linspace(0, x.size/fs, x.size)  
        #
        #figure()
        #
        #subplot(2,1,1)
        #plot(t, x)
        #ylabel('amplitude')
        #title('%s waveform' % filename)
        #ylim(-1.0, 1.0)
        #plot_onsets(t, ploc, 'r')  
        #plot_gt(onsets_gt)
        #axhline(color='black') # y=0
        #
        #subplot(2,1,2)
        #plot(t, mixcoef*norm_f0_interp, 'b')
        #plot(t, (1-mixcoef)*norm_e, 'g')
        #plot(t, decision, 'r')
        #xlabel('time (s)')
        #title('decision funcion')
        #ylim(0.0, 1.0)
        #plot(t[ploc], decision[ploc], 'o', color='r')
        #plot_onsets(t, ploc, 'r')
        #plot_gt(onsets_gt)
        #axhline(threshold, color='green', linestyle='--') # threshold line   

import operator        
for t in arange(0.9, 1.3, 0.05):
    s_fmeasure = array([])
    s_precision = array([])
    s_recall = array([])
    for n in filenames:
        f = 'melody%s' % n
        s_fmeasure = append(s_fmeasure, fmeasures[f][t])
        s_precision = append(s_precision, precisions[f][t])
        s_recall = append(s_recall, recalls[f][t])
    print 'fm %s\t | mean: %s\t | std: %s' % (t, s_fmeasure.mean(), s_fmeasure.std())  
    print 'pre %s\t | mean: %s\t | std: %s' % (t, s_precision.mean(), s_precision.std())
    print 'rec %s\t | mean: %s\t | std: %s' % (t, s_recall.mean(), s_recall.std())
    
figure()
t = linspace(0, 1, 500)
plot(t, abs(t))
plot(t, t**2)
plot(t, 10*log10(t))
xlabel('original waveform values')
ylabel('descriptor')
title('energy descriptors comparison')    
    