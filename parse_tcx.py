# -*- coding: utf-8 -*-
'''
Partial parser for Garmin Connect tcx files. Returns a Pandas DataFrame.
'''
import os
import sys
import lxml.etree
import numpy as np
import pandas as pd


def get_activity_type(root, garmin_ns):
    node = root.find(garmin_ns + 'Activity')
    return node.attrib['Sport']


def calculate_speed(distance, time):
    dt = time.diff().astype('timedelta64[s]')
    speed = 3.6*distance.diff()/dt
    return speed


def calculate_slope(distance, altitude):
    dx = distance.diff()
    dy = altitude.diff()
    slope = 180/np.pi * np.arctan2(dy, dx)
    return slope


def parse_cycling(root, garmin_ns):
    df = pd.DataFrame()
    for tp in root.findall(garmin_ns + 'Trackpoint'):
        row_data = {}
        for c in tp.getchildren():
            name = c.tag.split('}')[1]
            if 'Time' in name:
                row_data[name] = pd.to_datetime(c.text)
            elif 'Position' in name:
                continue
            elif 'HeartRateBpm' in name:
                row_data[name] = float(c.getchildren()[0].text)
            else:
                try:
                    row_data[name] = float(c.text)
                except:
                    pass
        row = pd.Series(row_data)
        df = df.append(row, ignore_index=True)

        df['Cadence'] = np.nan
    return df


def parse_running(root, garmin_ns):
    df = pd.DataFrame()
    for tp in root.findall(garmin_ns + 'Trackpoint'):
        row_data = {}
        for c in tp.getchildren():
            name = c.tag.split('}')[1]
            if 'Time' in name:
                row_data[name] = pd.to_datetime(c.text)
            elif 'Position' in name:
                tpx = c.getchildren()[0]
                row_data['Latitude'] = float(c.getchildren()[0].text)
                row_data['Longitude'] = float(c.getchildren()[1].text)
            elif 'HeartRateBpm' in name:
                row_data[name] = float(c.getchildren()[0].text)
            elif 'Extensions' in name:
                tpx = c.getchildren()[0]
                for c2 in tpx:
                    if 'Cadence' in c2.tag:
                        row_data['Cadence'] = 2*float(c2.text)
            else:
                try:
                    row_data[name] = float(c.text)
                except:
                    pass
        row = pd.Series(row_data)
        df = df.append(row, ignore_index=True)

    return df


def load_tcx_data(filename):
    root = lxml.etree.parse(filename).getroot()
    garmin_ns = './/{{{0}}}'.format(root.nsmap[None])
    activity_type = get_activity_type(root, garmin_ns)
    print('Activity type: ', activity_type)
    if activity_type == 'Running':
        df = parse_running(root, garmin_ns)
    elif activity_type == 'Biking':
        df = parse_cycling(root, garmin_ns)
    else:
        raise RuntimeError('Activity not implemented yet: {0}'.format(activity_type))

    seconds_since = (df['Time'] - df['Time'][0]).astype('timedelta64[s]')
    df['SecondsElapsed'] = seconds_since

    speed = calculate_speed(df['DistanceMeters'], df['Time'])
    df['Speed'] = speed

    slope = calculate_slope(df['DistanceMeters'], df['AltitudeMeters'])
    df['Slope'] = slope

    return df


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
        df = load_tcx_data(filename)
        print('Storing data to HDF5 file: ', filename_df)
        df.to_hdf(filename_df, 'ActivityData')

    return df


if __name__ == '__main__':
    df = load_tcx_data(sys.argv[1])
    print(df.describe())

