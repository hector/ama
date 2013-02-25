# -*- coding: utf-8 -*-
# Key profile extraction from mirex database
from pylab import *
import csv

filenames = range(1,97)
chroma_methods = ('ellis', 'toolbox_cp', 'toolbox_clp', 'toolbox_cens', 'toolbox_crp', 'hpcp')
notes = ('C','C#','D','D#','E','F','F#','G','G#','A','A#','B')
notes_b = ('C','Db','D','Eb','E','F','Gb','G','Ab','A','Bb','B')

pcps = {} # Variable to save the pitch class profiles extracted
for chroma_method in chroma_methods: 
    pcps[chroma_method] = {}
    pcps[chroma_method] = {'major': zeros(12), 'minor': zeros(12)}

for filename in filenames:
    gt_path = '../mirex_key/ground_truth/%02d.txt' % filename # path to ground truth file    
    gt_key, gt_mode = open(gt_path).readline().split() # e.g. gt_key = 'Bb' | gt_mode = 'major'
    
    try:
        offset = notes.index(gt_key)
    except ValueError: # search in bemols list
        offset = notes_b.index(gt_key)
    
    for chroma_method in chroma_methods:
        # from csv to array
        #data = loadtxt('%s_csv/%02d.csv' % (chroma_method, filename), delimiter=',').transpose()        
        #chroma = data[1:data.shape[1], :]        
        #chroma_avg = chroma.mean(1) # Average all chromas to a single PCP
        chroma_avg = genfromtxt('%s_csv/%02d_avg.csv' % (chroma_method, filename), delimiter=',')
        
        if offset != 0: 
            chroma_shifted = empty_like(chroma_avg)
            chroma_shifted[:-offset] = chroma_avg[offset:]
            chroma_shifted[-offset:] = chroma_avg[:offset]
            chroma_avg = chroma_shifted
            
        pcps[chroma_method][gt_mode] += chroma_avg.tolist()
    
# Save result to a file encoded as json
import json
for chroma_method in chroma_methods: # numpy arrays are not serializable 
    pcps[chroma_method]['major'] = (pcps[chroma_method]['major'] / max(abs(pcps[chroma_method]['major'])) ).tolist()
    pcps[chroma_method]['minor'] = (pcps[chroma_method]['minor'] / max(abs(pcps[chroma_method]['minor'])) ).tolist()

with open('PCPs.json', 'w') as file: file.write(json.dumps(pcps, sort_keys=True, indent=4, separators=(',', ': ')))
    