#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 2015/07/14

@author: samejima
'''

import numpy as np
from numpy.random import *
from scipy import stats
import pandas
import matplotlib.pyplot as plt
import statsmodels.api as sm


def GenData0():
    
    ac_server1 =[]
    ac_server2 =[]
    
    wl_server1=[]
    wl_server2=[]
    wl_server3=[]
    wl_server4=[]
    
    fp = open('../data/epa-http.txt', 'r')
    for line in fp.readlines():
        access = line.rstrip("\n").split("\t")
        ac_server1.append(access[1])
    fp.close()
    
    fp = open('../data/sdsc_http.txt', 'r')
    for line in fp.readlines():
        access = line.rstrip("\n").split("\t")
        ac_server2.append(access[1])
    fp.close()
    
    wl_server1 = GenWorkload(np.array([ac_server1]), 
                             [[0.4, 0.02]],
                              [[0, 0]])
     
    wl_server2 = GenWorkload(np.array([ac_server2]),
                              [[0.3, 0.03]],
                               [[0, 0]])
    wl_server3 = GenWorkload(np.array([ac_server1,ac_server2]), 
                             [[0.4, 0.01],[0.2, 0.01]], 
                             [[0, 0],[0, 0]])
    wl_server4 = GenWorkload(np.array([ac_server1,ac_server2]),
                              [[0.2, 0.01],[0.2, 0.01]], 
                              [[0, 0],[0, 0]])
    
    return np.array([wl_server1,wl_server2,wl_server3,wl_server4])
    
def GenWorkload(ac_mat, load_mat, delay_mat):
    
    # Length of time-series data. Generally 1440 (24hours *60 min)   
    length = ac_mat.shape[1]
    # The number of edges to the node including the node itself.
    # minimum number of edges = 1 (the node itself)
    n_edge = ac_mat.shape[0]
    
    wl_list = np.zeros((length))
    
    for l in range(length):
        for e in range(n_edge):
            
            if load_mat[e][1] >0:
                load = normal(load_mat[e][0],load_mat[e][1])
            else:
                load = load_mat[e][0]
            if delay_mat[e][1] >0:
                delay = normal(delay_mat[e][0],delay_mat[e][1])
            else:
                delay = delay_mat[e][0]
                
            # delay must be over 0 and integer
            if delay < 0: delay = 0
            else: delay = round(delay)
            
            # Consider only when delayed workload is within the given time-series data 
            if l+delay <= length: wl_list[l+delay] += float(ac_mat[e,l])*load
            else: continue
            
    return wl_list
    
    
if __name__ == '__main__':
    wl_mat = GenData0()
    
    for wl_list in wl_mat:
        for wl in wl_list:
            print wl,
        print 
    