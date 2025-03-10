# Quick script to overplot power colour values
# Written by David Gardenier, 2015-2016

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import math
from pyx import *

from filter_bursts import filter_bursts

def path(o):
    return '/scratch/david/master_project/' + o + '/info/database_' + o + '.csv'


def findbestres(res):
    '''Find the smallest resolution from a list of resolutions'''

    # Split resolutions into values and units
    heads = []
    tails = []
    for s in res:
        unit = s.strip('0123456789')
        num = s[:-len(unit)]
        heads.append(num)
        tails.append(unit)

    # Sort by unit, then by value
    unitorder = ['us','ms','s']
    for u in unitorder:
        if u in tails:
            indices = [i for i, x in enumerate(tails) if x==u]
            sameunits = [heads[i] for i in indices]
            sortvalues = sorted(sameunits)
            return sortvalues[0]+u


def findbestdataperobsid(df):
    '''Select the data with best mode and resolution'''
    ordering = ['gx1','gx2','event','binned','std2']
    for mode in ordering:
        if mode in df.modes.values:
            df = df[df.modes==mode]
            if df.shape[0] > 1:
                bestres = findbestres(df.resolutions.values)
                return df[df.resolutions==bestres].iloc[0]
            else:
                return df.iloc[0]


def findbestdata(db):
    # Apply constraint to the data
    db = db[(db.pc1.notnull() & db.lt3sigma==True)]
    db = db.groupby('obsids').apply(findbestdataperobsid)
    return db


def plot_allpcs():
    import numpy as np
    import itertools

    objects=[
            ('4U_0614p09', '4U 0614+09'),
            ('4U_1636_m53', '4U 1636-53'),
            ('4U_1702m43', '4U 1702-43'),
            ('4u_1705_m44', '4U 1705-44'),
            ('4U_1728_34', '4U 1728-34'),
            ('aquila_X1', 'Aql X-1'),
            ('cyg_x2', 'Cyg X-2'),
            ('gx_17p2', 'GX 17+2'),
            ('gx_340p0', 'GX 340+0'),
            ('gx_349p2', 'GX 349+2'), #Only 3 points
            ('gx_5m1', 'GX 5-1'), # Only 4 points
            ('HJ1900d1_2455', 'HETE J1900.1-2455'),
            ('IGR_J00291p5934', 'IGR J00291+5934'),
            ('IGR_J17498m2921', 'IGR J17498-2921'), #Only 1 point
            ('KS_1731m260', 'KS 1731-260'),
            ('xte_J1808_369', 'SAX J1808.4-3648'),
            ('S_J1756d9m2508', 'SWIFT J1756.9-2508'),
            ('sco_x1', 'Sco X-1'),
            ('sgr_x1', 'Sgr X-1'),
            ('sgr_x2', 'Sgr X-2'),
            ('v4634_sgr', 'V4634 Sgr'),
            ('XB_1254_m690', 'XB 1254-690'), #Only 1 point
            ('xte_J0929m314', 'XTE J0929-314'),
            ('J1701_462', 'XTE J1701-462'),
            ('xte_J1751m305', 'XTE J1751-305'),
            ('xte_J1807m294', 'XTE J1807-294'), # Only 2 points
            ('xte_J1814m338', 'XTE J1814-338'),  # Only 3 points
            ('gx_339_d4', 'GX 339-4'), # BH system
            ('H1743m322', 'H1743-322'),  # BH system
            ('xte_J1550m564', 'XTE J1550-564'), #BH system
            ]

    # Set up plot details

    for i, o in enumerate(objects):
        print o[-1]
        name = o[-1]
        o = o[0]
        p = path(o)
        db = pd.read_csv(p)
        db = findbestdata(db)
        db = filter_bursts(db)

        x = db.pc1.values
        y = db.pc2.values
        xerror = db.pc1_err.values
        yerror = db.pc2_err.values

        #colour = color.cmyk(0,0.87,0.68,0.32)
        colour = color.rgb.red
        g = graph.graphxy(height=4,
                          width=6,
                          x=graph.axis.log(min=0.03, max=250, title=r"PC1"),
                          y=graph.axis.log(min=0.01, max=20, title=r"PC2"))
        g.plot(graph.data.values(x=x, y=y, dx=xerror, dy=yerror), [graph.style.symbol(symbolattrs=[colour],size=0.1), graph.style.errorbar(size=0,errorbarattrs=[colour])])
        #g.text(5.7,3.5, name, [text.halign.boxright])
        outputfile = '/scratch/david/master_project/plots/publication/pc/individual/' + o
        g.writePDFfile(outputfile)
        os.system('convert -density 300 '+outputfile+'.pdf -quality 90 '+outputfile+'.png')
        # Subplots
        #plt.errorbar(x, y, xerr=xerror, yerr=yerror, fmt='o', linewidth=2)

        # plt.axis([0.01, 1000, 0.01, 100])
        # plt.xlabel('PC1 (C/A = [0.25-2.0]/[0.0039-0.031])')
        # plt.xscale('log', nonposx='clip')
        # plt.ylabel('PC2 (B/D = [0.031-0.25]/[2.0-16.0])')
        # plt.yscale('log', nonposy='clip')
        # plt.title('Power Colours')
        # plt.legend(loc='best', numpoints=1)
        #
        # # In case you want to save each figure individually
        # fig.tight_layout(pad=0.1)
        # plt.savefig('/scratch/david/master_project/plots/publication/pc/individual/' + o + '.pdf', transparent=True)
        # plt.gcf().clear()
        #plt.clf()

    #plt.show()

if __name__=='__main__':
    plot_allpcs()
