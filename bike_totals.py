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
datefilt = sys.argv[3]

# list tcx files
FileNames=glob.glob(os.path.join(TCXDirectory,datefilt + '*Cycling*.tcx'))

print(len(FileNames),' Files found')

all_HR=list([])
all_slope=list([])
all_cadence=list([])
all_speed=list([])
Duration=0
ElGain=0
ElLoss=0
c=0
for F in range(len(FileNames)):
    filename = FileNames[F]

    # Load TCX file activity data.
    # Then store it as a HDF5 file.
    # If HDF5 file already exists, load data from there.
    basenameIN = os.path.basename(filename)

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

    HR_TF='HeartRateBpm' in df.columns
    if HR_TF==False:
        continue

    HR=list(df['HeartRateBpm'])

    df['Mins']=df['SecondsElapsed']/60
    df['Hrs']=df['Mins']/60
    Duration+=df['Hrs'].max()

    Eldiff=np.diff(df['AltitudeMeters'])
    ElGain_=Eldiff[Eldiff>0]
    ElGain+=ElGain_.sum()
    ElLoss_=np.abs(Eldiff[Eldiff<0])
    ElLoss+=ElLoss_.sum()

    all_HR=np.append(HR,all_HR)

    SLOPE=list(df['Slope'])
    all_slope=np.append(SLOPE,all_slope)

    CADENCE=list(df['Cadence'])
    all_cadence=np.append(CADENCE,all_cadence)

    SPEED=list(df['Speed'])
    all_speed=np.append(SPEED,all_speed)

    c+=1

print('Data extracted.')

all_slope=all_slope[all_HR>0]
all_speed=all_speed[all_HR>0]
all_cadence=all_cadence[all_HR>0]
all_HR=all_HR[all_HR>0]

MIN_SPEED=6
MAX_SPEED=20

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

axes[0,0].hist(all_HR,bins=np.linspace(50,200,70))
axes[0,0].set_xlabel('Heart rate [bpm]')
axes[0,0].set_xlim([50,200])
statsbox(all_HR,[0,0])

axes[1,0].hist(all_cadence,bins=np.linspace(50,200,60))
axes[1,0].set_xlabel('Cadence')
statsbox(all_cadence,[1,0])
axes[1,0].set_xlim([60,200])

axes[2,0].hist(all_speed,bins=np.linspace(MIN_SPEED,MAX_SPEED,50))
axes[2,0].set_xlabel('Speed')
statsbox(all_speed,[2,0])

axes[3,0].scatter(all_slope,all_speed,c=all_HR,s=100,vmin=50,vmax=200,marker='.',alpha=0.1)
axes[3,0].set_xlabel('Slope')
axes[3,0].set_ylabel('Speed')
axes[3,0].set_ylim([MIN_SPEED,MAX_SPEED])
axes[3,0].set_xlim([-45,45])

for i in range(4):
    axes[i,1].set_axis_off()

print(c)

textstr = 'Summary for: ' + datefilt + '\n\n%0.0f activities totalling %0.2f hrs.\nElevation gain: %0.0f m\nElevation loss: %0.0f m'%(c,Duration, ElGain, ElLoss)
props = dict(boxstyle='round', alpha=0.5, color='w')
axes[0,1].text(0.3, 0.5, textstr, transform=axes[0,1].transAxes, fontsize=12,verticalalignment='center', bbox=props, fontweight='bold',horizontalalignment='left')

OutputFileName=os.path.join(outpath,'Bike-Summary-' + datefilt + '.png')

plt.savefig(OutputFileName)
plt.close()
