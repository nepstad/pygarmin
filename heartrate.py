# -*- coding: utf-8 -*-
'''
Analysis and calculation tools related to heart rate.

Heart rate zones
----------------
Various methods exists for calculating heart rate zones: Lactate
Threshold, Kavonen, Five Zone Method, ...
'''
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import interpolate
import parse_tcx

pd.options.display.mpl_style = 'default'

def get_time_in_zones(hrseries, zones):
    '''Calculate total time in each given heart rate zone.'''
    #Interpolate to constant time segments
    tstart = hrseries.index[0]
    tend = hrseries.index[-1]
    ntimes = hrseries.size
    interp_times = np.linspace(tstart, tend, ntimes)
    print(tstart, tend)
    dt = interp_times[1] - interp_times[0]
    hrseries_interp = interpolate.UnivariateSpline(hrseries.index,
                                                   hrseries,
                                                   s=0.0, k=3)
    hrseries_interp = hrseries_interp(interp_times)

    counts, bins = np.histogram(hrseries, bins=[0] + list(zones))
    tiz = pd.DataFrame(index=zones.index,
                       columns=['ZoneStart', 'ZoneEnd', 'TimeInZone'])
    tiz['TimeInZone'] = counts / counts.sum()*100
    tiz['ZoneStart'][1:] = zones[:-1]
    tiz['ZoneEnd'][:] = zones[:]

    return tiz


def get_zones_lactate_thresh(lt, hrmin, hrmax):
    '''Calculate the five zones based on lactate threshold (LT)'''
    zones_dict = {'Recovery': 0.8*lt,
                  'Aerobic': 0.88*lt,
                  'Threshold': 0.94*lt,
                  'Lactate': lt,
                  'VO2Max': 1.05*lt,
                  'Speed': hrmax}
    zones = pd.Series(zones_dict)
    zones.sort(inplace=True)
    return zones


def get_zones_kavonen_five(hrmin, hrmax):
    hrr = hrmax - hrmin
    zones_dict = {'Warmup': hrmin + 0.6*hrr,
                  'Recover': hrmin + 0.7*hrr,
                  'Aerobic': hrmin + 0.8*hrr,
                  'Anaerobic': hrmin + 0.9*hrr,
                  'Redline': hrmin + hrr}
    zones = pd.Series(zones_dict)
    zones.sort(inplace=True)
    return zones


if __name__ == '__main__':
    hrmin = float(sys.argv[2])
    hrmax = float(sys.argv[3])
    lt = float(sys.argv[4])
    df = parse_tcx.get_activity_data(sys.argv[1])
    times = df.SecondsElapsed
    hrseries = pd.Series(index=times, data=df['HeartRateBpm'].values)
    zones = get_zones_lactate_thresh(lt, hrmin, hrmax)
    zones_kavonen = get_zones_kavonen_five(hrmin, hrmax)
    tiz = get_time_in_zones(hrseries, zones)
    tizkav = get_time_in_zones(hrseries, zones_kavonen)
    fig, ax = plt.subplots(1, 3, figsize=(15,5))
    tiz['TimeInZone'].plot(ax=ax[0], kind='barh')
    tizkav['TimeInZone'].plot(ax=ax[1], kind='barh')
    df['HeartRateBpm'].plot(ax=ax[2], kind='kde')
    df['HeartRateBpm'].plot(ax=ax[2], kind='hist', normed=True,
        bins=np.linspace(hrmin, hrmax, (hrmax-hrmin)//2), alpha=0.3)
    print(tiz)
    print(tizkav)
    plt.tight_layout()
    plt.show()
    input()
