# -*- coding: utf-8 -*-
from pylab import *
from distutils.dir_util import mkpath
import csv 
import json

filenames = range(1,97) #97
#filenames = [88]

# Chroma extraction strategies
chroma_methods = ('ellis', 'toolbox_cp', 'toolbox_clp', 'toolbox_cens', 'toolbox_crp', 'hpcp')
# Notes
notes = ('C','C#','D','D#','E','F','F#','G','G#','A','A#','B')
notes_b = ('C','Db','D','Eb','E','F','Gb','G','Ab','A','Bb','B')
# Key profiles
key_profiles = {'krumhansl': { # Krumhansl and Kessler’s
                    'major': [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88],
                    'minor': [6.33, 2.68, 3.52, 5.38, 2.6, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]},
                'diatonic': {
                    'major': [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
                    'minor': [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1]}, # harmonic minor
                'temperley': {
                    'major': [5.0, 2.0, 3.5, 2.0, 4.5, 4.0, 2.0, 4.5, 2.0, 3.5, 1.5, 4.0],
                    'minor': [5.0, 2.0, 3.5, 4.5, 2.0, 4.0, 2.0, 4.5, 3.5, 2.0, 1.5, 4.0]},
                'composite': {
                    'major': [5.0, 0.0, 3.5, 0.0, 4.5, 4.0, 0.0, 4.5, 0.0, 3.5, 0.0, 4.0],
                    'minor': [5.0, 0.0, 3.5, 4.5, 0.0, 4.0, 0.0, 4.5, 3.5, 0.0, 0.0, 4.0]}}
                                        
key_profiles.update(json.loads(open('PCPs.json').read()))

# Results
results = {}
for chroma_method in chroma_methods: 
    results[chroma_method] = {}
    for key_profile in key_profiles.keys():
        results[chroma_method][key_profile] = 0

def print_pcp(pcp):
    "Print a bar chart that represents the global PCP"
    fig = figure()
    ax = fig.add_subplot(111)
    ax.bar(range(size(pcp)), pcp)
    ax.set_xticks(arange(0.4,12.4))
    ax.set_xticklabels(notes)    

def print_chroma(chroma):
    'Print chroma'
    fig_chroma = figure()
    ax = fig_chroma.add_subplot(111)
   
    ax.set_yticks(range(12))
    ax.set_yticklabels(('C','C#','D','D#','E','F','F#','G','G#','A','A#','B'))
    title("Chromagram | %s.wav" % filename)
    ylabel('note'); xlabel('time (s)') 


for filename in filenames:
    gt_path = '../mirex_key/ground_truth/%02d.txt' % filename # path to ground truth file    
    gt_key, gt_mode = open(gt_path).readline().split() # e.g. gt_key = 'Bb' | gt_mode = 'major'
    
    for chroma_method in chroma_methods:
        # from csv to array
        #data = genfromtxt('%s_csv/%02d.csv' % (chroma_method, filename), delimiter=',').transpose()                
        #t = data[0,:] # time values
        #chroma = data[1:data.shape[1], :]        
        #chroma_avg = chroma.mean(1) # Average all chromas to a single PCP
        chroma_avg = genfromtxt('%s_csv/%02d_avg.csv' % (chroma_method, filename), delimiter=',')        
        
        #chroma_avg[chroma_avg < mean(chroma_avg)] = 0
        #chroma_avg = chroma_avg - min(chroma_avg)
        #chroma_avg = chroma_avg * max(M) / float(max(chroma_avg))
        chroma_minus_mean = chroma_avg - mean(chroma_avg)
        var_chroma = std(chroma_avg)
        chroma_minus_var = chroma_avg - var_chroma
        
        for key_profile in key_profiles.keys():
            M = key_profiles[key_profile]['major']
            m = key_profiles[key_profile]['minor']
            mean_M = mean(M)
            var_M = std(M) 
            mean_m = mean(m)
            var_m = std(m)
            vars_times_M = var_chroma * var_M
            vars_times_m = var_chroma * var_m
            corr_M = empty(12)
            corr_m = empty(12)
            
            for i in range(12): # iterate over 12 semitones (0==C to 11==B)
                pcp_M = concatenate((M[-i:], M[:-i])) # Pitch Class Profile Major
                pcp_m = concatenate((m[-i:], m[:-i])) # Pitch Class Profile minor
                
                # Methods that search for the max:                
                # Correlation <-- Best one
                corr_M[i] = sum(chroma_minus_mean * (pcp_M - mean_M)) / float(vars_times_M)
                corr_m[i] = sum(chroma_minus_mean * (pcp_m - mean_m)) / float(vars_times_m)
                # Weighted sum
                #corr_M[i] = sum(chroma_avg * pcp_M)
                #corr_m[i] = sum(chroma_avg * pcp_m)  
                
                # Methods that search for the min:
                # Distance
                #corr_M[i] = sum(abs(chroma_avg - pcp_M))
                #corr_m[i] = sum(abs(chroma_avg - pcp_m))  
                # Nearest neighbor
                #corr_M[i] = sum((chroma_avg - pcp_M)**2)
                #corr_m[i] = sum((chroma_avg - pcp_m)**2) 
                # Euclidean distance <-- gives same results that NN
                #corr_M[i] = sqrt(sum((chroma_avg - pcp_M)**2))
                #corr_m[i] = sqrt(sum((chroma_avg - pcp_m)**2))

                
            key_M = argmax(corr_M) # predicted major key
            key_m = argmax(corr_m) # predicted minor key
            if corr_M[key_M] >= corr_m[key_m]:
                mode = 'major'
                key = key_M
            else:
                mode = 'minor'
                key = key_m
            
            if (notes[key] == gt_key or notes_b[key] == gt_key) and gt_mode == mode:
                results[chroma_method][key_profile] += 1
            
            #print 'File: %02d.wav' % filename
            #print 'OUR:\t%s\t%s' % (notes[key], mode)
            #print 'GT:\t%s\t%s\n' % (gt_key, gt_mode)
            
#==============================================================================
# Output results to a JSON file
#==============================================================================
# Add percentage
for chroma_method in chroma_methods: 
    for key_profile in key_profiles.keys():
        results[chroma_method][key_profile] = { 'hits': results[chroma_method][key_profile],
                                                'percentage': 100 * results[chroma_method][key_profile] / float(size(filenames)) }
                                                
with open('results.json', 'w') as file: file.write(json.dumps(results, sort_keys=True, indent=4, separators=(',', ': ')))                                                
         