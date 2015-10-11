# -*- coding: utf-8 -*-
'''
Create map with activity position points, colored by speed.
'''
import sys
import matplotlib
matplotlib.use('agg')
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.io.img_tiles import StamenTerrain, GoogleTiles, MapQuestOSM
import parse_tcx


def activity_map_figure(df):
    #Some position shorthands
    lon = df['Longitude']
    lat = df['Latitude']
    dlon = 0.1*(lon.max() - lon.min())
    dlat = 0.1*(lat.max() - lat.min())

    #Set up Cartopy map tiles, using OpenStreetMap
    tiler = MapQuestOSM()
    fig = plt.figure()

    units = ['km/h', 'bpm']
    columns = ['Speed', 'HeartRateBpm']
    for i, (unit, col) in enumerate(zip(units, columns)):
        ax = fig.add_subplot(1, 2, i+1, projection=tiler.crs)
        ax.set_extent((lon.min()-dlon, lon.max()+dlon,
                       lat.min()-dlat, lat.max()+dlat))
        ax.add_image(tiler, 15)

        #Plot activity positions on map, color by speed
        im = ax.scatter(df['Longitude'], df['Latitude'], c=df[col],
                transform=ccrs.Geodetic(), s=40, edgecolor='none',
                cmap=plt.cm.hot_r, alpha=0.5)
        ax.set_title('Mean = {0:.1f} [{1}]'.format(df[col].mean(), unit))
        cbar = plt.colorbar(im, shrink=.5, drawedges=False)
        cbar.set_label('{0} [{1}]'.format(col, unit))
        cbar.solids.set_rasterized(True)
        cbar.solids.set_edgecolor('face')
    #plt.suptitle('{0:.2f} km, {1:.1f} min'.format(
    #    df['DistanceMeters'].max()/1000,
    #    df['SecondsElapsed'].max()/60))
    return fig

if __name__ == '__main__':
    pd.options.display.mpl_style = 'default'
    filename = sys.argv[1]
    basename = filename[:-4]
    df = parse_tcx.get_activity_data(filename)
    print('Plotting maps')
    fig = activity_map_figure(df)
    plt.tight_layout()
    fig.savefig(basename + '-mapspeed.png', dpi=200)
    plt.close(fig)
