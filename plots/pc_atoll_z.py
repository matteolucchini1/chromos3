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

ns=[
    # ('4U_0614p09', '4U 0614+09'),
    # ('4U_1636_m53', '4U 1636-53'),
    # ('4U_1702m43', '4U 1702-43'),
    # ('4u_1705_m44', '4U 1705-44'),
    # ('4U_1728_34', '4U 1728-34'),
    # ('aquila_X1', 'Aql X-1'),
    # ('cyg_x2', 'Cyg X-2'),
    # ('gx_17p2', 'GX 17+2'),
    # ('gx_340p0', 'GX 340+0'),
    #('gx_349p2', 'GX 349+2'), #Only 3 points
    # ('gx_5m1', 'GX 5-1'),  # Only 4 points
    ('HJ1900d1_2455', 'HETE J1900.1-2455'),
    ('IGR_J00291p5934', 'IGR J00291+5934'),
    #('IGR_J17498m2921', 'IGR J17498-2921'), #Only 1 point
    # ('KS_1731m260', 'KS 1731-260'),
    ('xte_J1808_369', 'SAX J1808.4-3648'),
    ('S_J1756d9m2508', 'SWIFT J1756.9-2508'),
    # ('sco_x1', 'Sco X-1'),
    # ('sgr_x1', 'Sgr X-1'),
    # ('sgr_x2', 'Sgr X-2'),
    # ('v4634_sgr', 'V4634 Sgr'),
    #('XB_1254_m690', 'XB 1254-690'), #Only 1 point
    ('xte_J0929m314', 'XTE J0929-314'),
    ('J1701_462', 'XTE J1701-462'),
    ('xte_J1751m305', 'XTE J1751-305'),
    #('xte_J1807m294', 'XTE J1807-294'), # Only 2 points
    #('xte_J1814m338', 'XTE J1814-338'),  # Only 3 points
    #('gx_339_d4', 'GX 339-4'), # BH system
    #('H1743m322', 'H1743-322'),  # BH system
    #('xte_J1550m564', 'XTE J1550-564'), #BH system
    ]
x_ns = []
y_ns = []
xerror_ns = []
yerror_ns = []

for i, o in enumerate(ns):
    name = o[-1]
    o = o[0]
    p = path(o)
    db = pd.read_csv(p)
    db = findbestdata(db)
    db = filter_bursts(db)

    x_ns.extend(db.pc1.values)
    y_ns.extend(db.pc2.values)
    xerror_ns.extend(db.pc1_err.values)
    yerror_ns.extend(db.pc2_err.values)


def plot_allpcs():
    import numpy as np
    import itertools

    atolls=[('4u_1705_m44', '4U 1705-44'),
            ('4U_0614p09', '4U 0614+09'),
            ('4U_1636_m53', '4U 1636-53'),
            ('4U_1702m43', '4U 1702-43'),
            ('4U_1728_34', '4U 1728-34'),
            ('aquila_X1', 'Aql X-1'),
            ('KS_1731m260', 'KS 1731-260'),
            ('sgr_x1', 'Sgr X-1'),
            ('v4634_sgr', 'V4634 Sgr'),
            ('XB_1254_m690', 'XB 1254-690')
            ]

    zs = [('cyg_x2', 'Cyg X-2'),
          ('gx_5m1', 'GX 5-1'),
          ('gx_17p2', 'GX 17+2'),
          ('gx_340p0', 'GX 340+0'),
          ('gx_349p2', 'GX 349+2'),
          ('sco_x1', 'Sco X-1'),
          ('sgr_x2', 'Sgr X-2')]

    # Set up plot details
    g = graph.graphxy(height=7,
                      width=7,
                      x=graph.axis.log(min=0.01, max=300, title=r"PC1"),
                      y=graph.axis.log(min=0.01, max=100, title=r"PC2"),
                      key=graph.key.key(pos='tr', dist=0.2))
    errstyle= [graph.style.symbol(graph.style.symbol.changesquare, size=0.1, symbolattrs=[color.gradient.Rainbow]),
               graph.style.errorbar(size=0,errorbarattrs=[color.gradient.Rainbow])]
    scatterstyle= [graph.style.symbol(graph.style.symbol.changeplus,size=0.15, symbolattrs=[color.gradient.Rainbow])]

    x_atolls = []
    y_atolls = []
    xerror_atolls = []
    yerror_atolls = []

    for i, o in enumerate(atolls):
        print o[-1]
        name = o[-1]
        o = o[0]
        p = path(o)
        db = pd.read_csv(p)
        db = findbestdata(db)
        db = filter_bursts(db)

        x_atolls.extend(db.pc1.values)
        y_atolls.extend(db.pc2.values)
        xerror_atolls.extend(db.pc1_err.values)
        yerror_atolls.extend(db.pc2_err.values)

    # Plot Neutron Stars
    grey= color.cmyk(0,0,0,0.5)
    nsstyle = [graph.style.symbol(size=0.1, symbolattrs=[grey])]
    g.plot(graph.data.values(x=x_ns, y=y_ns, title='Neutron Stars'), nsstyle)

    # Plot Atolls
    g.plot(graph.data.values(x=x_atolls, y=y_atolls, title='Atoll sources'), scatterstyle)

    #plot Black Holes
    x_z = []
    y_z = []
    xerror_z = []
    yerror_z = []

    for i, o in enumerate(zs):
        print o[-1]
        name = o[-1]
        o = o[0]
        p = path(o)
        db = pd.read_csv(p)
        db = findbestdata(db)
        db = filter_bursts(db)

        x_z.extend(db.pc1.values)
        y_z.extend(db.pc2.values)
        xerror_z.extend(db.pc1_err.values)
        yerror_z.extend(db.pc2_err.values)

    # Plot Z
    g.plot(graph.data.values(x=x_z, y=y_z, title='Z sources'), scatterstyle)

    g.writePDFfile('/scratch/david/master_project/plots/publication/pc/atoll_z')

if __name__=='__main__':
    plot_allpcs()
