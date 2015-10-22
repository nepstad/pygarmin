# -*- coding: utf-8 -*-
'''
Analysis of all run data in specified directory of tcx files.
'''
import sys
import os
import matplotlib
matplotlib.use('agg')
import pandas as pd
import matplotlib.pyplot as plt
import parse_tcx
import numpy as np
import datetime
from ipdb import set_trace as debug
import glob

def statsbox(var,ax):
    #VAR=df[var]
    VAR=var[var>0]
    #VAR=np.ma.masked_equal(VAR,0)
    VARmean = VAR.mean()
    VARmin = VAR.min()
    VARmax = VAR.max()
    textstr = 'Min=%.2f\nMean=%.2f\nMax=%.2f'%(VARmin, VARmean, VARmax)
    props = dict(boxstyle='round', alpha=0.5, color='w')
    axes[ax[0],ax[1]].text(1.1, 0.5, textstr, transform=axes[ax[0],ax[1]].transAxes, fontsize=10, verticalalignment='center', bbox=props)


pd.options.display.mpl_style = 'default'

# Path to tcx directory assumed to be passed as cmd line argument
TCXDirectory = sys.argv[1]
outpath = sys.argv[2]

# list tcx files
FileNames=glob.glob(os.path.join(TCXDirectory,'2015-08*Trail*unning*.tcx'))

print(len(FileNames),' Files found')

all_HR=list([])
all_slope=list([])
all_cadence=list([])
all_speed=list([])
for F in range(len(FileNames)):
    filename = FileNames[F]

    # Load TCX file activity data.
    # Then store it as a HDF5 file.
    # If HDF5 file already exists, load data from there.
    basenameIN = os.path.basename(filename)
    if os.path.basename(filename)=='2015-08-24_Trondheim Trail Running_Running.tcx':
        continue

    print(F)
    print(filename)

    basenameOUT = os.path.join(outpath, basenameIN[:-4])

    filename_df = basenameOUT + '.h5'
    if os.path.exists(filename_df):
        print('Loading data from HDF5 file')
        df = pd.read_hdf(filename_df, 'ActivityData')
    else:
        df = parse_tcx.load_tcx_data(filename)

        print('Storing data to HDF5 file: ', filename_df)
        df.to_hdf(filename_df, 'ActivityData')

    HR=list(df['HeartRateBpm'])

    all_HR=np.append(HR,all_HR)

    SLOPE=list(df['Slope'])
    all_slope=np.append(SLOPE,all_slope)

    CADENCE=list(df['Cadence'])
    all_cadence=np.append(CADENCE,all_cadence)

    SPEED=list(df['Speed'])
    all_speed=np.append(SPEED,all_speed)

print('Data extracted.')

all_slope=all_slope[all_HR>0]
all_speed=all_speed[all_HR>0]
all_cadence=all_cadence[all_HR>0]
all_HR=all_HR[all_HR>0]

MIN_SPEED=6
MAX_SPEED=22

all_slope=all_slope[all_speed>MIN_SPEED]
all_cadence=all_cadence[all_speed>MIN_SPEED]
all_HR=all_HR[all_speed>MIN_SPEED]
all_speed=all_speed[all_speed>MIN_SPEED]

all_slope=all_slope[all_speed<MAX_SPEED]
all_cadence=all_cadence[all_speed<MAX_SPEED]
all_HR=all_HR[all_speed<MAX_SPEED]
all_speed=all_speed[all_speed<MAX_SPEED]

plt.close("all")
fig, axes = plt.subplots(4, 2, figsize=(10, 10))

axes[0,0].hist(all_HR,bins=np.linspace(all_HR.min(),all_HR.max(),60))
axes[0,0].set_xlabel('Heart rate [bpm]')
statsbox(all_HR,[0,0])

axes[1,0].hist(all_cadence,bins=np.linspace(all_cadence.min(),all_cadence.max(),50))
axes[1,0].set_xlabel('Cadence')
statsbox(all_cadence,[1,0])

axes[2,0].hist(all_speed,bins=np.linspace(MIN_SPEED,MAX_SPEED,50))
axes[2,0].set_xlabel('Speed')
statsbox(all_speed,[2,0])

axes[3,0].scatter(all_slope,all_speed,c=all_HR,s=80,vmin=50,vmax=200,marker='.',alpha=0.1)
axes[3,0].set_xlabel('Slope')
axes[3,0].set_ylabel('Speed')
axes[3,0].set_ylim([MIN_SPEED,MAX_SPEED])

for i in range(4):
    axes[i,1].set_axis_off()

plt.savefig('/home/emlynd/Desktop/test.png')
plt.close()
