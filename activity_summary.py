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

print(df)

# Basic statistics as html document
print('Basic statistics')
df.describe().to_html(basename + '-statistics.html')

df['Mins']=df['SecondsElapsed']/60
hr_zones=np.linspace(0,210,100)

# Plot heart rate data
print('Heart rate plot')
fig, axes = plt.subplots(4, 2, figsize=(10, 10))
axes[0,0].plot(df['Mins'], df['HeartRateBpm'],linewidth=0.8, alpha=0.5)
axes[0,0].set_ylabel('Heart rate [bpm]')
axes[0,1].hist(df['HeartRateBpm'],bins=hr_zones)
axes[0,1].set_xlabel('Heart rate [bpm]')

axes[1,0].plot(df['Mins'],df['Speed'],linewidth=0.8, alpha=0.5)
axes[1,0].set_ylabel('Speed [km/h]')
#axes[1,1].hist(df['Speed'])

axes[1,1].scatter(df['Slope'],df['Speed'],c=df['HeartRateBpm'],s=60,vmin=50,vmax=200,marker='.',alpha=0.5)
axes[1,1].set_xlabel('Slope')
axes[1,1].set_ylabel('Speed')

axes[2,0].plot(df['Mins'],df['Cadence'],linewidth=0.8, alpha=0.5, marker='.', linestyle='none',markersize=2)
axes[2,0].set_ylabel('Cadence [smp]')
axes[2,1].hist(df['Cadence'],bins=np.linspace(0,200,100))
axes[2,1].set_xlabel('Cadence')

#axes[3,0].plot(df['Mins'],df['AltitudeMeters'],linewidth=0.8, alpha=0.5)
axes[3,0].scatter(df['Mins'],df['AltitudeMeters'],c=df['HeartRateBpm'],s=60,vmin=50,vmax=200,marker='.',alpha=0.5)
axes[3,0].set_ylabel('Altitude [m]')
axes[3,1].hist(df['AltitudeMeters'])
axes[3,1].set_xlabel('Altitude')
axes[3,0].set_xlabel('Minutes')

for i in range(4):
    axes[i,0].set_xlim(0,df['Mins'].max())

plt.savefig(basename + '-heartrate.png')
plt.close()
