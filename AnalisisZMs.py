import sys
from datetime import date, timedelta
from numpy import cumsum, arange, array, savetxt, mean, loadtxt, zeros, quantile
from scipy.stats import beta, geom
from matplotlib import use
from matplotlib.pyplot import subplots, rcParams, close, plot
from pandas import datetime, read_excel, read_csv, Timestamp
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import AutoMinorLocator
import datetime as dt
import pickle
from covid_mcmc import covid_mcmc2
import numpy as np


def ReadInfoZMs(filename='data/Configuracion.csv', delim=',', workdir="./../"):
    mapeo = {}
    file1 = open(workdir + filename, 'r')
    count = 0

    while True:
        count += 1
        line = file1.readline()
        if not line:
            break
        sline = line.strip()
        data = sline.split(',')
        mapeo[data[0]] = data[1:]
        mapeo[data[0]][2] = int(mapeo[data[0]][2])

        for i in range(4, len(data)):
            dateString = data[i].split(' ')
            mapeo[data[0]][i-1] = date(int(dateString[0]), int(dateString[1]), int(dateString[2]))
        mapeo[data[0]].append("None")
    file1.close()
    return mapeo


def AnalyzeZM(clave, trim, court, init0, init_index0, size_window, exit_probs, R_rates_V2, Pobs_I, Pobs_D, delta_day, num_data, workdir="./../"):
    data_fnam = clave + '.csv'
    init = init0 + timedelta(days=court * (size_window - 1))
    init_index = (init - ZMs[clave][3]).days

    if trim == 0:
        out_fnam = clave
    else:
        out_fnam = clave+"_trim%d" % (trim,)
    intervention_day = [(d - ZMs[clave][3]).days - delta_day for d in ZMs[clave][4:-(int(ZMs[clave][1]) + 1)]][0]


    if  init_index0 + intervention_day > init_index > 0:
        intervention_day = delta_day + (intervention_day - init_index)
    else:
        intervention_day=0
    print("day",intervention_day)

    exit_probs_copy = exit_probs
    N = ZMs[clave][2]

    zm = covid_mcmc2(Region=ZMs[clave][0], init_day=ZMs[clave][3], data_fnam=data_fnam,\
        N=N, out_fnam=out_fnam, init_index=init_index, init=init, init_index0=init_index0, init0=init0,\
        intervention_day=intervention_day, trim=trim, Pobs_I=Pobs_I, Pobs_D=Pobs_D, exit_probs=exit_probs_copy,\
                     R_rates=R_rates_V2, court=court, size_window=size_window, num_data=num_data,
                     delta_day=delta_day, workdir=workdir)
    return zm



dateparse = lambda x: datetime.strptime(x, '%Y-%m-%d') #datos Reg IRAG


def PlotFigsZMs(zm, pred, court,q=[10,25,50,75,90], blue=True, workdir='./../'):
    close('all')
    out_fnam = zm.out_fnam
    #-----------------------------------------------------------
    fig, ax = subplots(num=1, figsize=(8, 6))
    zm.PlotEvolution(pred=pred, cumm=False, log=False, ty=0, ax=ax, q=q, blue=blue, add_MRE=True,\
        label=r'Mediana', csv_fnam=workdir + "csv/%s_court_%s_I.csv" % (out_fnam, court))
    fig.tight_layout()
    fig.savefig("%s%s_court_%s_I.png" % (workdir + 'figs/', out_fnam, court))
    # -----------------------------------------------------------
    fig, ax = subplots(num=2, figsize=(8, 6))
    zm.PlotEvolution(pred=pred, cumm=False, log=False, ty=1, ax=ax, q=q, blue=blue,\
        label=r'Mediana', right_axis=False, csv_fnam="../csv/%s_court_%s_D.csv" % (out_fnam,court))
    fig.tight_layout()
    fig.savefig("%s%s_court_%s_D.png" % (workdir + 'figs/', out_fnam, court))
    #------------------------------------------------------------
    fig, ax = subplots(num=3, figsize=(8, 6))
    zm.plot_cones(pred=pred, ty=0, cumm=False, log=False, ax=ax,
                  q=q, blue=blue, color='red', color_q='black',
                  label=True, right_axis=False)
    fig.tight_layout()
    fig.savefig("%s%s_court_%s_I_cono.png" % (workdir + 'figs/', out_fnam, court))

    #------------------------------------------------------------
    fig, ax = subplots(num=3, figsize=(8, 6))
    zm.plot_cones(pred=pred, ty=0, cumm=False, log=False, ax=ax,
                  q=q, blue=blue, color='red', color_q='black',
                  label=True, right_axis=False)
    fig.tight_layout()
    fig.savefig("%s%s_court_%s_D_cono.png" % (workdir + 'figs/', out_fnam, court))
    return ax


def ClaveZM(nombre, ZMs):
    clave_match = ''
    for clave in ZMs.keys():
        if ZMs[clave][0].find(nombre) != -1:
            print("%4s: %s" % (clave, ZMs[clave][0]))
            clave_match = clave
    return clave_match


def all_predictions(T, clave, num_data, size_window, pred, R_rates, all_pred, forecast, workdir = "./../"):

    data_fnam = clave + '.csv'
    Init0 = ZMs[clave][3]
    init0 = Init0 + timedelta(days=10)
    init_index0 = (init0 - ZMs[clave][3]).days
    data = np.loadtxt(workdir + 'data/' + data_fnam)
    court = (data[init_index0:].shape[0] - num_data) // (size_window - 1) + 1
    res = (data[init_index0:].shape[0] - num_data) % (size_window - 1)
    init0 = init0 + timedelta(days=res)
    init_index0 = (init0 - ZMs[clave][3]).days
    delta_day = 10 + res
    i = 0
    if all_pred==True:
        while i < 2:
            ZMs[clave][-1] = AnalyzeZM(clave, trim=0, court=i, init0=init0, init_index0=init_index0, size_window=size_window,
                                       exit_probs=exit_probs, R_rates_V2=R_rates, Pobs_I=Pobs_I, Pobs_D=Pobs_D, delta_day=delta_day,
                                       num_data=num_data)
            ZMs[clave][-1].clave = clave
            zm = ZMs[clave][-1]
            x0 = zm.sim_init()
            xp0 = zm.sim_init()
            if zm.support(x0) and zm.support(xp0):
                zm.RunMCMC(T=T, x0=x0, xp0=xp0, pred=pred, plot_fit=False)
                PlotFigsZMs(zm, pred=pred, court=i, blue=True)
                i = i + 1

    else:
        ZMs[clave][-1] = AnalyzeZM(clave, trim=0, court=court + forecast, init0=init0, init_index0=init_index0,
                                   size_window=size_window, exit_probs=exit_probs, R_rates_V2=R_rates, Pobs_I=Pobs_I, Pobs_D=Pobs_D,
                                   delta_day=delta_day, num_data=num_data)
        ZMs[clave][-1].clave = clave
        zm = ZMs[clave][-1]
        x0 = zm.sim_init()
        xp0 = zm.sim_init()

        while (zm.support(x0) and zm.support(xp0))==False:
            x0 = zm.sim_init()
            xp0 = zm.sim_init()


        zm.RunMCMC(T=T, x0=x0, xp0=xp0, pred=pred, plot_fit=False)
        PlotFigsZMs(zm, pred=pred, court=i, blue=True)

ZMs = ReadInfoZMs()
num_data = 35
exit_probs = [0.1, 1]
Pobs_I = 0.85
Pobs_D = 0.9
pred = 21
size_window = 8
T = 5000
R_rates = {'E': [1/5, r'\sigma_1',  2], 'I^S': [1/13, r'\sigma_2',  2], 'I^A': [1/7, r'\gamma_1', 2]}
rcParams.update({'font.size': 12})
q = [10, 25, 50, 75, 90]

clave=['AS','BC','BS','CC','CS', 'CH','CL','CM','DG','GT','GR','HG','JC','9-01','MN',
       'MS','MC','NT','NL','OC','PL','QT','QR','SP','SL','SR','TC','TS','TL','VZ','YN','ZS']
for i in range(1):
    all_predictions(T=T, clave=clave[i], num_data=num_data, size_window=size_window,
                pred=pred, R_rates=R_rates, all_pred=True, forecast=0)
