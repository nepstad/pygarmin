# -*- coding: utf-8 -*-
'''
Create map with activity position points, colored by speed.
'''
import sys
import os
import matplotlib
matplotlib.use('agg')
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.io.img_tiles import StamenTerrain, GoogleTiles, MapQuestOSM
import parse_tcx

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

#Some position shorthands
lon = df['Longitude']
lat = df['Latitude']
dlon = 0.1*(lon.max() - lon.min())
dlat = 0.1*(lat.max() - lat.min())

#Set up Cartopy map tiles, using OpenStreetMap
print('Plotting')
tiler = MapQuestOSM()
fig = plt.figure(figsize=(10,8))
ax = fig.add_subplot(1, 1, 1, projection=tiler.crs)
ax.set_extent((lon.min()-dlon, lon.max()+dlon,
               lat.min()-dlat, lat.max()+dlat))
ax.add_image(tiler, 15)

#Plot activity positions on map, color by speed
im = ax.scatter(df['Longitude'], df['Latitude'], c=df['Speed'],
        transform=ccrs.Geodetic(), s=20, edgecolor='none',
        cmap=plt.cm.hot_r)
cbar = plt.colorbar(im, shrink=.9)
cbar.set_label('Speed [m/s]')
plt.savefig(basename + '-mapspeed.png', dpi=200)
plt.close()
