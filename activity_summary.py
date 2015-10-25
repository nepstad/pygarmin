# -*- coding: utf-8 -*-
'''
Create a meso-scale report (figures, html document) of a Garmin activity.
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


def statsbox(var,ax):
    VAR=df[var]
    VAR=VAR[VAR>0]
    #VAR=np.ma.masked_equal(VAR,0)
    VARmean = VAR.mean()
    VARmin = VAR.min()
    VARmax = VAR.max()
    textstr = var + ':\nMin=%.2f\nMean=%.2f\nMax=%.2f'%(VARmin, VARmean, VARmax)
    props = dict(boxstyle='round', alpha=0.5, color='w')
    axes[ax[0],ax[1]].text(1.1, 0.5, textstr, transform=axes[ax[0],ax[1]].transAxes, fontsize=10,
                verticalalignment='center', bbox=props)


pd.options.display.mpl_style = 'default'


#Path to tcx file assumed to be passed as cmd line argument
filename = sys.argv[1]

# Load TCX file activity data.
# Then store it as a HDF5 file.
# If HDF5 file already exists, load data from there.
basename = filename[:-4]
filename_df = basename + '.h5'
if os.path.exists(filename_df):
    print('Loading data from HDF5 file')
    df = pd.read_hdf(filename_df, 'ActivityData')
else:
    df = parse_tcx.load_tcx_data(filename)
    print('Storing data to HDF5 file: ', filename_df)
    df.to_hdf(filename_df, 'ActivityData')

# print(df)

# Basic statistics as html document
print('Basic statistics')
df.describe().to_html(basename + '-statistics.html')

df['Mins']=df['SecondsElapsed']/60

# Plot heart rate data
print('Heart rate plot')
fig, axes = plt.subplots(4, 3, figsize=(15, 10))
#axes[0,0].plot(df['Mins'], df['HeartRateBpm'],linewidth=0.8, alpha=0.5)
axes[0,0].scatter(df['Mins'],df['HeartRateBpm'],c=df['HeartRateBpm'],s=80,vmin=50,vmax=200,marker='.',alpha=0.5)
axes[0,0].set_ylabel('Heart rate [bpm]')
axes[0,1].hist(df['HeartRateBpm'],bins=np.linspace(df['HeartRateBpm'].min(),df['HeartRateBpm'].max(),50))
axes[0,1].set_xlabel('Heart rate [bpm]')
statsbox('HeartRateBpm',[0,1])

axes[1,0].plot(df['Mins'],df['Speed'],linewidth=0.8, alpha=0.5)
axes[1,0].set_ylabel('Speed [km/h]')
#axes[1,1].hist(df['Speed'])

axes[1,1].scatter(df['Slope'],df['Speed'],c=df['HeartRateBpm'],s=60,vmin=50,vmax=200,marker='.',alpha=1)
axes[1,1].set_xlabel('Slope')
axes[1,1].set_ylabel('Speed')
statsbox('Speed',[1,1])

axes[2,0].plot(df['Mins'],df['Cadence'],linewidth=0.8, alpha=0.5, marker='.', linestyle='none',markersize=2)
axes[2,0].set_ylabel('Cadence [spm]')
Cad=df['Cadence']
Cad=np.array(Cad[Cad>0])
axes[2,1].hist(Cad,bins=np.linspace(Cad.min(),Cad.max(),50))
axes[2,1].set_xlabel('Cadence')
statsbox('Cadence',[2,1])

#axes[3,0].plot(df['Mins'],df['AltitudeMeters'],linewidth=0.8, alpha=0.5)
axes[3,0].scatter(df['Mins'],df['AltitudeMeters'],c=df['HeartRateBpm'],s=80,vmin=50,vmax=200,marker='.',alpha=0.5)
axes[3,0].set_ylabel('Altitude [m]')
axes[3,1].hist(df['AltitudeMeters'])
axes[3,1].set_xlabel('Altitude')
axes[3,0].set_xlabel('Minutes')
statsbox('AltitudeMeters',[3,1])

axes[0,2].set_axis_off()
axes[1,2].set_axis_off()
axes[2,2].set_axis_off()
axes[3,2].set_axis_off()

textstr = df['Time'].min().strftime('%d/%m/%Y %H:%M') + '-' + df['Time'].max().strftime('%H:%M')
props = dict(boxstyle='round', alpha=0.5, color='w')
axes[0,1].text(0.5, 1.2, textstr, transform=axes[0,1].transAxes, fontsize=12,
            verticalalignment='center', bbox=props, fontweight='bold', horizontalalignment='center')

Duration=df['Mins'].max()

Eldiff=np.diff(df['AltitudeMeters'])

ElGain=Eldiff[Eldiff>0]
ElGain=ElGain.sum()

ElLoss=np.abs(Eldiff[Eldiff<0])
ElLoss=ElLoss.sum()

textstr = 'Total time: %0.0f mins.\nElevation gain: %0.0f m\nElevation loss: %0.0f m'%(Duration, ElGain, ElLoss)
props = dict(boxstyle='round', alpha=0.5, color='w')
axes[2,2].text(0.5, 0.5, textstr, transform=axes[2,2].transAxes, fontsize=12,
            verticalalignment='center', bbox=props, fontweight='bold', horizontalalignment='left')

for i in range(4):
    axes[i,0].set_xlim(0,df['Mins'].max())

plt.savefig(basename + '-ActivitySummary.png')
plt.close()
