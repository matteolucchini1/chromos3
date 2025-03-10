# Quick script to overplot power colour values
# Written by David Gardenier, 2015-2016

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import math
from collections import defaultdict
from scipy.stats import binned_statistic
import numpy as np
from pyx import *

ns={'4u_1705_m44':'4U 1705-44',
        '4U_0614p09':'4U 0614+09',
        '4U_1636_m53':'4U 1636-53',
        '4U_1702m43':'4U 1702-43',
        '4U_1728_34':'4U 1728-34',
        'aquila_X1':'Aql X-1',
        'cyg_x2':'Cyg X-2',
        'gx_5m1':'GX 5-1',
        'gx_17p2':'GX 17+2',
        'gx_339_d4':'GX 339-4', #BH system
        'gx_340p0':'GX 340+0',
        'gx_349p2':'GX 349+2',
        'HJ1900d1_2455':'HETE J1900.1-2455',
        'IGR_J00291p5934':'IGR J00291+5934',
        'IGR_J17498m2921':'IGR J17498-2921',
        'J1701_462':'XTE J1701-462',
        'KS_1731m260':'KS 1731-260',
        'sco_x1':'Sco X-1',
        'sgr_x1':'Sgr X-1',
        'sgr_x2':'Sgr X-2',
        'S_J1756d9m2508':'SWIFT J1756.9-2508',
        'v4634_sgr':'V4634 Sgr',
        'XB_1254_m690':'XB 1254-690',
        'xte_J0929m314':'XTE J0929-314',
        'xte_J1550m564':'XTE J1550-564', #BH system
        'xte_J1751m305':'XTE J1751-305',
        'xte_J1807m294':'XTE J1807-294',
        'xte_J1808_369':'SAX J1808.4-3648',
        'xte_J1814m338':'XTE J1814-338'}


def getdata(obj,obsid,mode):

    path = '/scratch/david/master_project/' + obj + '/P' + obsid[:5] + '/' + obsid + '/' +mode + '_*.ps'
    ps = glob.glob(path)

    # Import data
    try:
        all_data = np.loadtxt(ps[0],dtype=float)
        inverted_data = np.transpose(all_data)
    except IOError:
        print 'No power spectrum'
        return

    # Give the columns their names
    ps = inverted_data[0]
    ps_error = inverted_data[1]
    freq = inverted_data[2]
    freq_error = inverted_data[3]
    ps_squared = inverted_data[4]
    num_seg = inverted_data[5][0]

    freqps_err = []
    for i in range(len(freq)):
        err = math.fabs(freq[i]*ps[i])*math.sqrt((freq_error[i]/float(freq[i]))**2 + (ps_error[i]/float(ps[i]))**2 + 2*(freq_error[i]*ps_error[i])/float(freq[i]*ps[i]))
        freqps_err.append(err)

    bin_means, bin_edges, binnumber = binned_statistic(freq, freq*ps, bins=np.logspace(-3,2, num=50))
    counts, bin_edges, binnumber = binned_statistic(freq, freq*ps, statistic='count', bins=np.logspace(-3,2, num=50))

    bin_errs = []
    old_count = 0
    for c in counts:
        if c==0:
            bin_errs.append(0)
            continue
        c = int(c)
        indexes = [i for i in range(old_count,old_count+c)]
        bin_err = 1/float(c)*math.sqrt(sum([e**2 for i, e in enumerate(freqps_err) if i in indexes]))
        bin_errs.append(bin_err)
        old_count = c

    bin_centres = np.logspace(-2.95,2.05, num=50)

    return bin_means, bin_edges, bin_centres, bin_errs

class empty:

    def __init__(self):
        pass
    def labels(self, ticks):
        for tick in ticks:
            tick.label=""

def plotpsperhue(huerange,plotinfo):
    # Objects should be in the order top-left, top-right, bottom-left, bottom-right
    #if len(objects) != 4:
    #    return
    if len(plotinfo) == 4:
        plotinfo = [plotinfo[3], plotinfo[1], plotinfo[0], plotinfo[2]]

    allinfo = zip(*plotinfo)
    objects = allinfo[0]
    obsids = allinfo[1]
    modes = allinfo[2]

    # Set up plot details
    c=canvas.canvas()

    if len(plotinfo) == 4:
        xposition=[0.0,5.0,0.0,5.0]
        yposition=[0.0,0.0,4.5,4.5]
    if len(plotinfo) == 2:
        xposition=[0.0,5.0]
        yposition=[0.0,0.0]

    print huerange, '\n=========================='
    for i in range(len(objects)):
        obj = objects[i]
        obsid = obsids[i]
        mode = modes[i]

        print ns[obj]

        binmeans, binedges, bincentres, binerrs = getdata(obj,obsid,mode)
        nbinmeans = []
        for b in binmeans:
            if b < 1e-6 or math.isnan(b): #y axis limit
                nbinmeans.append(1e-6)
            else:
                nbinmeans.append(b)

        values = graph.data.values(x=binedges[:-1], y=nbinmeans)


        myticks = []
        if yposition[i]!=0.0:
            xtitle = " "
            xtexter=empty()
        else:
            xtitle = "Frequency (Hz)"
            xtexter=graph.axis.texter.mixed()
        if xposition[i]!=0.0:
            ytitle = ""
            ytexter=empty()
        else:
            ytitle="Power $\cdot$ Frequency"
            ytexter=graph.axis.texter.mixed()
            # myticks = [graph.axis.tick.tick(10e-6, label="10$^-6$", labelattrs=[text.mathmode]),
            #            graph.axis.tick.tick(10e-4, label="10$^-4$", labelattrs=[text.mathmode]),
            #            graph.axis.tick.tick(10e-2, label="10$^-2$", labelattrs=[text.mathmode])]
                       #graph.axis.tick.tick(0.8, label=" ", labelattrs=[text.mathmode])]
            #graph.axis.texter.mixed()

        g=c.insert(graph.graphxy(width=5.0,
                                 height=4.5,
                                 xpos=xposition[i],
                                 ypos=yposition[i],
                                 x=graph.axis.log(min=1e-2,max=60,title=xtitle,texter=xtexter),
                                 y=graph.axis.log(min=1e-6,max=0.8,title=ytitle,texter=ytexter)))

        if i == 2:
            g.plot(values,[graph.style.histogram(lineattrs=[color.rgb.black, style.linewidth.Thick,],autohistogrampointpos=0,fromvalue=1e-6,steps=1)])
        else:
            g.plot(values,[graph.style.histogram(lineattrs=[color.gradient.Rainbow, style.linewidth.Thick,],autohistogrampointpos=0,fromvalue=1e-6,steps=1)])
        errstyle= [graph.style.symbol(size=0.0, symbolattrs=[color.gradient.Rainbow]),
                   graph.style.errorbar(size=0.0,errorbarattrs=[color.rgb.red])]
        if i == 2:
            errstyle= [graph.style.symbol(size=0.0, symbolattrs=[color.rgb.black]),
                       graph.style.errorbar(size=0.0,errorbarattrs=[color.rgb.black])]
        g.plot(graph.data.values(x=bincentres[:-1], y=nbinmeans, dy=binerrs), errstyle)
        xtext, ytext = g.pos(0.014, 0.4)
        g.text(xtext,ytext, ns[obj], [text.halign.boxleft, text.valign.top])

    title = huerange.replace('_', '$^{\circ}$-') + '$^{\circ}$'
    c.text(5.0,yposition[-1]+4.5+0.3,title,
           [text.halign.center, text.valign.bottom, text.size.Large])

    outputfile = '/scratch/david/master_project/plots/publication/ps/%s' %huerange
    c.writePDFfile(outputfile)
    os.system('convert -density 300 '+outputfile+'.pdf -quality 90 '+outputfile+'.png')


def plot_ps():
    import numpy as np
    import itertools

    huerange = '0_20'
    objects = [('gx_339_d4','80132-01-23-01','event'),
               ('J1701_462', '92405-01-34-01', 'event'),
               ('IGR_J00291p5934', '90052-03-01-06', 'event'),
               ('4U_1636_m53','10088-01-09-00','event')]
    plotpsperhue(huerange,objects)

    huerange = '20_40'
    objects = [('gx_339_d4','91095-08-08-00','gx1'),
               ('J1701_462', '92405-01-42-06', 'event'),
               ('aquila_X1', '50049-01-03-01', 'event'),
               ('4U_0614p09', '30056-01-03-04', 'event')]
    plotpsperhue(huerange,objects)

    huerange = '40_60'
    objects = [('gx_339_d4','92704-03-18-00','event'),
               ('aquila_X1','94076-01-02-00','binned'),
               ('aquila_X1','40432-01-05-00','event'),
               ('J1701_462', '92405-01-17-12', 'event')]
    plotpsperhue(huerange,objects)

    huerange = '60_80'
    objects = [('gx_339_d4','95409-01-13-03','event'),
               ('S_J1756d9m2508','92050-01-01-01','event'),
               ('aquila_X1','50049-01-03-02','event'),
               ('J1701_462','92405-01-14-01','event')]
    plotpsperhue(huerange,objects)

    huerange = '80_100'
    objects = [('gx_339_d4','20183-01-02-00','gx1'),
               ('aquila_X1', '40033-10-02-04', 'event'),
               ('S_J1756d9m2508', '94065-06-02-02', 'event'),
               ('4u_1705_m44', '40051-03-02-00', 'event')]
    plotpsperhue(huerange,objects)

    huerange = '100_120'
    objects = [('gx_339_d4','95409-01-13-02','event'),
               ('HJ1900d1_2455', '96030-01-22-00', 'event'),
               ('S_J1756d9m2508', '94065-02-01-04', 'event'),
               ('aquila_X1', '40033-10-02-06', 'event')]
    plotpsperhue(huerange,objects)

    huerange = '120_140'
    objects = [('gx_339_d4','60705-01-69-00','gx1'),
               ('v4634_sgr', '20089-01-01-00', 'gx1'),
               ('HJ1900d1_2455', '92049-01-08-00', 'event'),
               ('aquila_X1', '40033-10-02-00', 'event')]
    plotpsperhue(huerange,objects)

    huerange = '140_160'
    objects = [('gx_339_d4','92035-01-03-00','event'),
               ('HJ1900d1_2455', '91057-01-05-01', 'event'),
               ('v4634_sgr', '92703-01-02-01', 'event'),
               ('aquila_X1', '50049-01-04-00', 'event')]
    plotpsperhue(huerange,objects)

    huerange = '160_180'
    objects = [('gx_339_d4','92035-01-03-06','event'),
               ('4U_0614p09', '10095-01-03-01', 'event'),
               ('aquila_X1', '93076-01-05-00', 'event'),
               ('4U_1728_34', '50030-03-10-00', 'event')]
    plotpsperhue(huerange,objects)

    huerange = '180_200'
    objects = [('gx_339_d4','92085-02-04-00','event'),
               ('gx_17p2', '20056-02-06-00', 'event'),
               ('cyg_x2', '30046-01-12-00', 'binned'),
               ('J1701_462', '91442-01-01-01', 'binned')]
    plotpsperhue(huerange,objects)

    huerange = '200_220'
    objects = [('gx_339_d4','70130-01-01-00','binned'),
               ('J1701_462', '91106-02-02-11', 'binned'),
               ('cyg_x2', '90030-01-56-01', 'binned'),
               ('sco_x1', '30035-01-09-00', 'binned')]
    plotpsperhue(huerange,objects)

    huerange = '220_240'
    objects = [('gx_339_d4','70109-01-13-00','binned'),
               ('sco_x1', '40020-01-03-00', 'binned'),
               ('cyg_x2', '91009-01-46-00', 'binned'),
               ('J1701_462', '91106-02-02-14', 'binned')]
    plotpsperhue(huerange,objects)

    huerange = '240_260'
    objects = [('gx_339_d4','95335-01-01-07','event'),
               ('cyg_x2', '90030-01-55-00', 'binned'),
               ('sco_x1', '40020-01-01-07', 'binned'),
               ('4U_0614p09', '40030-01-06-00', 'event')]
    plotpsperhue(huerange,objects)

    huerange = '260_280'
    objects = [('gx_339_d4','95409-01-15-06','event'),
               ('J1701_462','91106-01-12-00','binned'),
               ('sco_x1', '20053-01-01-05', 'binned'),
               ('cyg_x2', '90030-01-04-00', 'binned')]
    plotpsperhue(huerange,objects)

    huerange = '280_300'
    objects = [('gx_339_d4','95335-01-01-00','event'),
               ('cyg_x2', '90030-01-31-00', 'binned'),
               ('sco_x1', '20053-01-02-05', 'binned'),
               ('J1701_462','91106-02-03-14','binned')]
    plotpsperhue(huerange,objects)

    huerange = '300_320'
    objects = [('gx_339_d4','95409-01-16-05','event'),
               ('sco_x1','40706-01-03-00','binned'),
               ('cyg_x2', '30046-01-02-00', 'binned'),
               ('J1701_462', '92405-01-37-10', 'event')]
    plotpsperhue(huerange,objects)

    huerange = '320_340'
    objects = [('gx_339_d4','92035-01-04-00','binned'),
               ('J1701_462', '92405-01-15-00', 'event'),
               ('cyg_x2', '90030-01-32-00', 'binned'),
               ('sgr_x1', '40023-01-03-00', 'event')]
    plotpsperhue(huerange,objects)

    huerange = '340_360'
    objects = [('gx_339_d4','70109-01-02-00','event'),
               ('IGR_J00291p5934', '90425-01-02-05', 'event'),
               ('sgr_x2', '30051-01-03-00', 'binned'),
               ('aquila_X1','50049-02-08-03','event')]
    plotpsperhue(huerange,objects)


if __name__=='__main__':
    plot_ps()
