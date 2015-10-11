# -*- coding: utf-8 -*-
'''
Create a minimal report (figures, html document) of a Garmin activity.
'''
import sys
import os
import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
import parse_tcx


def get_activity_data(filename):
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


def minimal_report_figure(df):
    '''Plot heart rate data'''
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    df.plot(x='SecondsElapsed', y='HeartRateBpm', ax=axes[0],
            linewidth=0.8, alpha=0.5)
    hr_smoothed = pd.stats.moments.rolling_mean(df['HeartRateBpm'], 60)
    axes[0].plot(df['SecondsElapsed'], hr_smoothed, linewidth=1.6)
    df.hist(column='HeartRateBpm', ax=axes[1])
    axes[0].set_ylabel('Heart rate [bpm]')
    axes[1].set_xlabel('Heart rate [bpm]')
    return fig


if __name__ == '__main__':
    matplotlib.use('agg')
    pd.options.display.mpl_style = 'default'

    #Path to tcx file assumed to be passed as cmd line argument
    filename = sys.argv[1]
    basename = filename[:-4]
    df = get_activity_data(filename)

    # Basic statistics as html document
    print('Basic statistics')
    df.describe().to_html(basename + '-statistics.html')

    print('Heart rate plot')
    fig = minimal_report_figure(df)
    fig.savefig(basename + '-heartrate.png')
    plt.close(fig)

