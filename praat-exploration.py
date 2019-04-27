__author__ = 'Amogh Jalihal'

import parselmouth as pm
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import pandas as pd
HOME = os.path.expanduser('~')
from optparse import OptionParser

def parseArgs(args):
    parser = OptionParser()
    parser.add_option('-p', '--path', type='str',default='',
                      help='Path to audio file')
    (opts, args) = parser.parse_args(args)
    return opts, args

def main(args):
    opts, args = parseArgs(args)
    path = opts.path
    if path is None or len(path) == 0:
        print("Please specify path to Boolean model")
        sys.exit()
    if '~' in path:
        path = path.replace('~',HOME )
    fname = path.split('/')[-1]
    #######################################
    ## This is the base frequency
    ## Please set this manually
    base = 147.
    #########################################
    sound = pm.Sound(path)
    snd_part = sound.extract_part(from_time=15.,to_time=200., preserve_times=True)
    pitches = snd_part.to_pitch()
    intensity = snd_part.to_intensity()
    inten = intensity.values.T
    freq = pitches.selected_array['frequency']
    cleaned = np.array([[t,v] for t,(v,f) in enumerate(zip(freq,inten)) if v > 0.0 and f > 10 ])

    rel = []
    kt = [1,3,6,8,10]
    R = np.arange(-8,15)
    swars = ['s','_r','r','_g','g','m','m^','p','_d','d','_n','n']
    labels = []
    f,ax = plt.subplots()


    for i in R:
        rel.append(base*2.**(float(i/12.)))
        if i > 0:
            labels.append(swars[int(float(abs(i))%12.0)])
        else:
            labels.append(swars[int(float(abs(12+i))%12.0)])
        if float(abs(i))%12.0 == 0.0:
            ax.axhline(rel[-1],c='k',lw=5.)
        elif i > 0 and i in kt:
            ax.axhline(rel[-1],alpha=0.1,c='k')
        elif i < 0.0 and i + 12 in kt:
            ax.axhline(rel[-1],alpha=0.1,c='k')
        else:
            ax.axhline(rel[-1],c='r')
    ax.set_ylim([min(rel),max(rel)])
    ax.plot(cleaned[:,0],cleaned[:,1])
    ax.set_title(fname)
    ax2 = ax.twinx()
    voi = []
    swarsequence = []
    window = 3
    for c in cleaned:
        for r,l in zip(rel,labels):
            if c[1] > r-window and c[1] < r+window:
                voi.append(c)
                swarsequence.append([c[0],l])
    voi = np.array(voi)
    swarsequence = np.array(swarsequence)
    seqDF = pd.DataFrame(swarsequence,columns=['frame','swar'])
    seqDF.to_csv(fname + '_sequence.tsv',sep='\t',index=False)
    ax.plot(voi[:,0],voi[:,1],'r.')
    ticks= ax.get_yticks()
    leftlabel = ax.get_yticklabels()
    ax2.set_ylim([min(rel),max(rel)])
    ax2.set_yticks(rel)
    ax2.set_yticklabels(labels)
    
    plt.show()
    
if __name__ == '__main__':
    main(sys.argv)
