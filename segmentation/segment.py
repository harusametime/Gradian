#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 2015/07/14

@author: samejima
'''

import os.path
import numpy as np
from pystruct.models import GraphCRF
from pystruct.learners import FrankWolfeSSVM
from statsmodels.tsa.ar_model import AR
from statsmodels.tsa.arima_model import ARMA


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
                load = np.random.normal(load_mat[e][0],load_mat[e][1])
            else:
                load = load_mat[e][0]
            if delay_mat[e][1] >0:
                delay = np.random.normal(delay_mat[e][0],delay_mat[e][1])
            else:
                delay = delay_mat[e][0]
                
            # delay must be over 0 and integer
            if delay < 0: delay = 0
            else: delay = round(delay)
            
            # Consider only when delayed workload is within the given time-series data 
            if l+delay <= length: wl_list[l+delay] += float(ac_mat[e,l])*load
            else: continue
            
    return wl_list


def show_alldata(ts_list):
    for ts in ts_list:
        for s in ts:
            print s,
        print
        
def gen_CRFData(wl_mat, interval):
    length = wl_mat.shape(1)
    n_nodes = wl_mat.shape(0)
    print length
    if(length <= interval):
        print "interval is too long for length."
    else:
        X = np.array(np.zeros(n_nodes,interval)*(length-interval))
        #y = np.array(0*)
    
if __name__ == '__main__':
    
    datapath = "../data/alldata.txt";
    if  os.path.isfile(datapath):
        wl_mat = []
        fp = open(datapath, 'r')
        for line in fp.readlines():
            wl_list = line.rstrip("\n").split("\t")
            wl_mat.append(wl_list)
        wl_mat = np.array(wl_mat)
        fp.close()
    else:
        print "Generate data randomly and stored to " + datapath
        wl_mat = GenData0()
    
    show_alldata(wl_mat)
    
    '''
    X: Matrices of time-series CPU data of each server
       when t=[0, interval]            ... -> X[0]
             =[1, interval+1]          ... -> X[1]
             =...
             =[Length-interval-1, Length-1]    ... -> X[Length-interval-1]
             
       The number of Matrices is Length-interval.
       Shape of each X is (#server, interval)
           e.g.       t=Length-1    t=Length-2
           Server1    3.6[%]    4.5[%]...
           Server2    2.5[%]    4.4[%]...
           
    y: Arrays of CPU data of each server
       when t = interval + 1    ...   -> y[0]
              = interval + 2    ...   -> y[1]
       Shape of y is (#server, )
           e.g.        t=Length
           Server1    3.6[%]   
           Server2    2.5[%]   
    '''
    X, y = gen_CRFData(wl_mat,interval=5)
    
    model = GraphCRF(directed=True, inference_method="max-product")
    
    
    '''
    ar_model = AR(remove_trend(wl_mat[0]))
    arma_model = ARMA(wl_mat[0],order = (2,2))
    ar_res = ar_model.fit()
    arma_res = arma_model.fit()
    for wl in wl_mat[0]:
        print wl,
    print
    
    predict = ar_res.resid
    for pr in predict:
        print pr,
    print
    
    predict = arma_res.resid
    for pr in predict:
        print pr,
    print 
    
    
    for i in range(len(wl_mat[0])-1):
        wl_mat[0, i] = wl_mat[0, i]- wl_mat[0, i+1]
    
    ar_model = AR(wl_mat[0])
    arma_model = ARMA(wl_mat[0],order = (2,2))
    ar_res = ar_model.fit()
    arma_res = arma_model.fit()
    for wl in wl_mat[0]:
        print wl,
    print
    
    predict = ar_res.resid
    for pr in predict:
        print pr,
    print
    '''    
    
    
    