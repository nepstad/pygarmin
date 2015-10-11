# -*- coding: utf-8 -*-
'''
Create a multi-page PDF report of a Garmin activity.
'''
import sys
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import datetime
from matplotlib.backends.backend_pdf import PdfPages
import minimalreport
import activitymap
import parse_tcx


def main(filename):
    #Set A4 figure size
    plt.rc('figure', figsize=(11.69, 8.27), dpi=100)

    basename = filename[:-4]
    df = parse_tcx.get_activity_data(filename)
    with PdfPages(basename + '-ActivitySummary.pdf') as pdf:
        print('Maps')
        mapfig = activitymap.activity_map_figure(df)
        plt.tight_layout()
        pdf.savefig(mapfig)
        plt.close(mapfig)

        print('Minimal report')
        mr_fig = minimalreport.minimal_report_figure(df)
        plt.tight_layout()
        pdf.savefig(mr_fig)
        plt.close(mr_fig)

        info = pdf.infodict()
        info['CreationDate'] = datetime.datetime.today()


if __name__ == '__main__':
    filename = sys.argv[1]
    main(filename)
