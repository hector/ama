# -*- coding: utf-8 -*-
from pylab import *
import os
from distutils.dir_util import mkpath
import csv
#from utils import *
#from descriptors import *   

folder = "hpcp_csv" # directory where CSVs wibe created
#filenames = ('melody4', 'ALoDown-mono', '07', 'extrabits')
filenames = range(1,97) #97
transfile = 'hpcp.n3' # use the same for all melodies   

for filename in filenames:    
    path = '../mirex_key/audio/%02d.wav' % filename # path to audio file
    mkpath(folder) # create dir for ouput. this does not fail if dir already exists
    os.system("rm %s/%02d_vamp_vamp-hpcp-mtg_MTG-HPCP_HPCP.csv" % (folder, filename)) # Remove if csv's already exist
    #os.system("/usr/local/bin/sonic-annotator -s vamp:vamp-hpcp-mtg:MTG-HPCP:HPCP > %s" % (transfile)) # create configuration file
    os.system("/usr/local/bin/sonic-annotator -t %s %s -w csv --csv-basedir %s" % (transfile, path, folder)) # extract features

    # We want to reorder the data so columns are output in the form: time, C, C#, D, ..., B
    data = genfromtxt("%s/%02d_vamp_vamp-hpcp-mtg_MTG-HPCP_HPCP.csv" % (folder, filename), delimiter=',')
    chroma = data.copy()
    chroma[:, 1:data.shape[1]-3] = data[:, 4:data.shape[1]]
    chroma[:, data.shape[1]-3:data.shape[1]] = data[:, 1:4]        # good?
    #savetxt("%s/%02d.csv" % (folder, filename), chroma, delimiter=',', fmt='%10.7f')
    savetxt("%s/%02d_avg.csv" % (folder, filename), mean(chroma[:, 1:],0), delimiter=',') # save key profile    
    
    os.system("rm %s/%02d_vamp_vamp-hpcp-mtg_MTG-HPCP_HPCP.csv" % (folder, filename))
    