#Co-written by I.Isturiz and H.Verwei, VHove based on F.Burla's notes
#Generalized by H.Verweii
from __future__ import division, unicode_literals, print_function  # for compatibility with Python 2 and 3

import matplotlib as mpl
import matplotlib.pyplot as plt

# change the following to %matplotlib notebook for interactive plotting



# Optionally, tweak styles.
mpl.rc('figure',  figsize=(10, 5))
mpl.rc('image', cmap='gray')

import numpy as np
import pandas as pd
from pandas import DataFrame, Series  # for convenience

#For ND2 files
from pims import ND2_Reader
from pims import ND2Reader_SDK

#For trackpy
import pims
import trackpy as tp


#Imports for van Hove
import matplotlib.mlab as mlab
import scipy.stats as ss
from scipy.stats import norm


import re as re
import seaborn as sns
import pickle

def save_obj(obj, name, folder ):
    with open(folder+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name, folder ):
    with open(folder + name + '.pkl', 'rb') as f:
        return pickle.load(f)

def track_particles_06(files, rad, numframes=1300, ml=500):

    '''This function takes .nd2 files as input and track particles over a given number of frames. This results in a data frame
    with the x and y position for each particle at each frame. This is safed in the ditionary called traject under the corresponding file name
    the ensamble MSD is calculated and the stretching exponent and transport factor, this is stored in the library ens_msd'''

    ens_msd={}
    traject={}
    videos=[]

    for file in files:
        print(file)
        sample=re.search('\d+_(\w+_[A-Z]_[\d]*).nd2', file).group(1)
        videos.append(sample)
        with ND2_Reader(f'{file}') as frames:


            f = tp.batch(frames[:numframes], rad+2, minmass=9000, threshold=200, processes='auto')
            #Link features into particle trajectories
            t = tp.link(f, 5, memory=3)

        #filter spurious trajectories
        t1 = tp.filter_stubs(t, 50)
        # Compare the number of particles in the unfiltered and filtered data.
        #print('Before:', t['particle'].nunique())
        #print('After:', t1['particle'].nunique())

        #plt.figure()
        # convenience function -- just plots size vs. mass
        #tp.mass_size(t1.groupby('particle').mean());

        t2 = t1[((t1['mass'] > 5000) & (t1['size'] < 2.4) &
                     (t1['ecc'] < 0.4))]
        traject[f"{sample}_traject"]=t2
        #d=tp.compute_drift(t2)
        #traject[f"{sample}_drift"]=d
        #traject[f"{sample}_driftcorrected"]=tp.subtract_drift(t2.copy(), d)

       # plt.figure()
       # plt.suptitle(f"{file}")

        #with ND2_Reader(f'{folder}/{file}') as frames:
            #tp.annotate(t2[t2['frame'] == 0], frames[0]);

        #plt.figure(figsize=(12,12))
        #plt.suptitle(f"Trajectories_{sample}")
        #tp.plot_traj(t2);

        ens_msd[f'{sample}_em'] = tp.emsd(t2, 166.56/512, 99.9, max_lagtime=ml)



        ens_msd[f'{sample}_fit']= tp.utils.fit_powerlaw(ens_msd[f'{sample}_em'])

    return ens_msd, traject, videos

def track_particles_p08(files, rad,numframes=1300, ml=500):

    '''This function takes .nd2 files as input and track particles over a given number of frames. This results in a data frame
    with the x and y position for each particle at each frame. This is safed in the ditionary called traject under the corresponding file name
    the ensamble MSD is calculated and the stretching exponent and transport factor, this is stored in the library ens_msd'''

    ens_msd={}
    traject={}
    videos=[]

    for file in files:
        print(file)
        sample=re.search('\d+_(\w+_[A-Z]_[\d]*).nd2', file).group(1)
        videos.append(sample)
        with ND2_Reader(f'{file}') as frames:


            f = tp.batch(frames[:numframes], rad+2, minmass=10000, threshold=300)
            #Link features into particle trajectories
            t = tp.link(f, 5, memory=3)

        #filter spurious trajectories
        t1 = tp.filter_stubs(t, 50)
        # Compare the number of particles in the unfiltered and filtered data.
        #print('Before:', t['particle'].nunique())
        #print('After:', t1['particle'].nunique())

        #plt.figure()
        # convenience function -- just plots size vs. mass
        #tp.mass_size(t1.groupby('particle').mean());

        t2 = t1[((t1['mass'] > 40000) & (t1['size'] < 3.0) &
                     (t1['ecc'] < 0.25))]
        traject[f"{sample}_traject"]=t2
        #d=tp.compute_drift(t2)
        #traject[f"{sample}_drift"]=d
        #traject[f"{sample}_driftcorrected"]=tp.subtract_drift(t2.copy(), d)

       # plt.figure()
       # plt.suptitle(f"{file}")

        #with ND2_Reader(f'{folder}/{file}') as frames:
            #tp.annotate(t2[t2['frame'] == 0], frames[0]);

        #plt.figure(figsize=(12,12))
        #plt.suptitle(f"Trajectories_{sample}")
        #tp.plot_traj(t2);

        ens_msd[f'{sample}_em'] = tp.emsd(t2, 166.56/512, 99.9, max_lagtime=ml)


        ens_msd[f'{sample}_fit']= tp.utils.fit_powerlaw(ens_msd[f'{sample}_em'])

    return ens_msd, traject, videos

def track_particles_p08_set2(files, ens_msd,traject,videos, rad,start=1301,numframes=2300, ml=500):

    '''This function takes .nd2 files as input and track particles over a given number of frames. This results in a data frame
    with the x and y position for each particle at each frame. This is safed in the ditionary called traject under the corresponding file name
    the ensamble MSD is calculated and the stretching exponent and transport factor, this is stored in the library ens_msd

    Note this one can be used for particles with a diameter of 0.8 um and 1.1 um you only have to adjust the radius'''



    for file in files:
        print(file)
        sample=re.search('\d+_(\w+_[A-Z]_[\d]*).nd2', file).group(1)
        sample=f'{sample}_2'
        if sample not in videos:
            videos.append(sample)
        with ND2_Reader(f'{file}') as frames:


            f = tp.batch(frames[start:numframes], rad+2, minmass=10000, threshold=300)
            #Link features into particle trajectories
            t = tp.link(f, 5, memory=3)

        #filter spurious trajectories
        t1 = tp.filter_stubs(t, 50)
        # Compare the number of particles in the unfiltered and filtered data.
        #print('Before:', t['particle'].nunique())
        #print('After:', t1['particle'].nunique())

        #plt.figure()
        # convenience function -- just plots size vs. mass
        #tp.mass_size(t1.groupby('particle').mean());

        t2 = t1[((t1['mass'] > 40000) & (t1['size'] < 3.0) &
                     (t1['ecc'] < 0.25))]
        traject[f"{sample}_traject"]=t2
        #d=tp.compute_drift(t2)
        #traject[f"{sample}_drift"]=d
        #traject[f"{sample}_driftcorrected"]=tp.subtract_drift(t2.copy(), d)

       # plt.figure()
       # plt.suptitle(f"{file}")

        #with ND2_Reader(f'{folder}/{file}') as frames:
            #tp.annotate(t2[t2['frame'] == 0], frames[0]);

        #plt.figure(figsize=(12,12))
        #plt.suptitle(f"Trajectories_{sample}")
        #tp.plot_traj(t2);

        ens_msd[f'{sample}_em'] = tp.emsd(t2, 166.56/512, 99.9, max_lagtime=ml)


        ens_msd[f'{sample}_fit']= tp.utils.fit_powerlaw(ens_msd[f'{sample}_em'])

    return ens_msd, traject, videos


def get_delta(sample, folder, times=[0.05,0.1,0.5,1.0]):

#dt is the time interval that you are considering.
#It is not a time, but the difference between the frames (so you need to convert it in time)

    list_dtframes=[int(t*100) for t in times]
    deltas={} #Initiate a library in which vectors with discplacements will be stored for different lag times
    for dt in  list_dtframes:
        lagtime=dt/99.9 #99.9 frames per second
        print(f'lagtime: {round(lagtime,2)} seconds')
        delta_r3  =[]
        for i in range (1,60000):
            #Loop over all the trajectories
            try:
                #i denotes the trajectory number, trajectories have been given a random number
                a = pd.read_csv(f'Trajectories/{folder}/{sample}_trajectory{i}.txt',delimiter='\t')
                #obtain the x and y coordinates
                x_load = a.x*66.56/512 #this would be a conversion of your real size vs pixel size
                y_load = a.y*66.56/512

                number=len(y_load)-dt


                if len(y_load)> dt:
                    for j in range(0,number):
                        zeta = y_load[j+dt]-y_load[j]
                        zeta2 = x_load[j+dt]-x_load[j]
                        delta_r3.extend((zeta,zeta2))
               # print(delta_r3)
            except OSError: pass
        deltas[f'{round(lagtime,2)}']= delta_r3
    return deltas


def vanHove(deltas, info, dia='0.6', times=[0.05,0.1,0.5,1.0], \
colorlist=['indianred','coral','yellowgreen','darkolivegreen', 'forestgreen','cornflowerblue', 'plum']):
    for i,lagtime in enumerate(times):
        print(f'Lagtime: {lagtime}')
        #Fit a gaussian to the data and extract mean and sigma
        (mu, sigma) = norm.fit(deltas[f'{lagtime}'])
        #Plot the real data
        n, bins = np.histogram(deltas[f'{lagtime}'],bins=150,density=True)
        #I think this shifts dsitribution so that it is centered at mu with std sigma
        y_g = norm.pdf(bins, mu, sigma)
        #l = plt.plot(bins, y_g, 'r--', linewidth=2)
        plt.yscale('log')
        plt.ylim(0,1)
        plt.xlim(-10,10)
        print (sigma)



        bincenters = 0.5*(bins[1:]+bins[:-1])
        p_0=max(y_g)
        plt.plot(bins, y_g/p_0,'--', color=colorlist[i], linewidth=2.)
        plt.scatter(bincenters,n/p_0, color=colorlist[i], label=f'dt={lagtime}s')
        plt.yscale('log')

    plt.title(f"van Hove distribution, particle diameter {dia} μm, {info}")
    plt.ylim(0.01,1.2)
    plt.xlabel("displacement (μm)")
    plt.ylabel('P(x)/P(0)')
    plt.xlim(-5,5)
    plt.legend()
    d=re.search('(\d)\.(\d)',dia).group(1)
    d2=re.search('(\d)\.(\d)',dia).group(2)
    plt.savefig(f'Particletrack/Figures/p{d}{d2}_Vimentin={info}.PNG')
    plt.show()
