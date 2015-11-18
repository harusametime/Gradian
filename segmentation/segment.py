#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 2015/07/14

@author: samejima
'''

import os.path
import numpy as np
import sys
import sklearn
from pystruct.models import GraphCRF
from pystruct.learners import FrankWolfeSSVM
from statsmodels.tsa.ar_model import AR
from statsmodels.tsa.arima_model import ARMA
from cv2 import inRange
from gtk.keysyms import End
from numpy.linalg.linalg import LinAlgError
from statsmodels.tsa.arima_model import ARIMA

import Image
import matplotlib.pyplot as plt
import numpy as np
from pygco import cut_simple

def example_binary():
    # generate trivial data
    x = np.ones((10, 10))
    x[:, 5:] = -1
    x_noisy = x + np.random.normal(0, 0.8, size=x.shape)
    x_thresh = x_noisy > .0

    # create unaries
    unaries = x_noisy
    # as we convert to int, we need to multipy to get sensible values
    unaries = (10 * np.dstack([unaries, -unaries]).copy("C")).astype(np.int32)
    # create potts pairwise
    pairwise = -10 * np.eye(2, dtype=np.int32)

    # do simple cut
    result = cut_simple(unaries, pairwise)
    
    print unaries
    print result


def example_multinomial():
    # generate dataset with three stripes
    np.random.seed(15)
    x = np.zeros((10, 12, 3))
    x[:, :4, 0] = -1
    x[:, 4:8, 1] = -1
    x[:, 8:, 2] = -1
    unaries = x + 1.5 * np.random.normal(size=x.shape)
    x = np.argmin(x, axis=2)
    unaries = (unaries * 10).astype(np.int32)
    x_thresh = np.argmin(unaries, axis=2)

    # potts potential
    pairwise_potts = -2 * np.eye(3, dtype=np.int32)
    result = cut_simple(unaries, 10 * pairwise_potts)
    # potential that penalizes 0-1 and 1-2 less thann 0-2
    pairwise_1d = -15 * np.eye(3, dtype=np.int32) - 8
    pairwise_1d[-1, 0] = 0
    pairwise_1d[0, -1] = 0
    print result
    result_1d = cut_simple(unaries, pairwise_1d)
    plt.subplot(141, title="original")
    plt.imshow(x, interpolation="nearest")
    plt.subplot(142, title="thresholded unaries")
    plt.imshow(x_thresh, interpolation="nearest")
    plt.subplot(143, title="potts potentials")
    plt.imshow(result, interpolation="nearest")
    plt.subplot(144, title="1d topology potentials")
    plt.imshow(result_1d, interpolation="nearest")
    plt.show()

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
    length = wl_mat.shape[1]
    n_nodes = wl_mat.shape[0]
    
    if(length <= interval):
        print "interval is too long for length."
        sys.exit()
    
    
    X = np.empty(length-interval,dtype=np.matrix)
    for i in range(length-interval):
        X[i] = np.array((wl_mat[:,i:i+interval]))
        
    y = np.empty(length-interval,dtype=np.matrix)
    
    for i in range(length-interval):
        y[i] = np.array((wl_mat[:,i+interval]))
        y[i] = y[i].T
    
    
    return X, y


def getLikelihood(endog,exog, order = None,n_forecasted_data=1):
    
    '''
    train_en = endog[:predict_start-1]
    test_en = endog[predict_start:]
    print train_en
    print test_en
    train_ex = exog[:predict_start-1]
    test_ex = exog[predict_start:]
    '''
    # Automatically determine values of orders
    if order is None:
        from scipy.optimize import brute
        grid = (slice(1, 3, 1), slice(1, 3, 1),slice(0, 3, 1))
        
        print "############################################"
        print endog
        print "############################################"
        
        try: 
            order =  brute(objfunc, grid, args=(exog, endog), finish=None)
            order = order.astype(int)
        except :
            order = [1,1,3]
        # Model fits given data (endog) with optimized order
        
        
    print "*********************************************"
    print "Choose order of ",
    print order
    print "*********************************************"
    
    model = ARIMA(endog,order).fit(full_output=False,disp=False)
    
    # 1st element of array x is the forecasted data.
    x = model.forecast(n_forecasted_data)
    return x[0]
    #likelihood = np.array.empty(len(endog))
    #for e in range(len(endog)):
    #    likelihood[e] = fit.
        
    

def objfunc(order,exog, endog):
    try:
        fit = ARIMA(endog, order).fit(full_output=False,fdisp=False)
        return fit.aic
    except:
        return sys.maxint



if __name__ == '__main__':
    
    
    
    datapath = "../data/anomaly30-20.txt";
    if  os.path.isfile(datapath):
        wl_mat = np.loadtxt(datapath)
    else:
        print "Generate data randomly and stored to " + datapath
        wl_mat = GenData0()
    
    show_alldata(wl_mat)
    '''
    wl_mat = np.rint(wl_mat*10).astype(int)
    wl_mat = wl_mat.astype(int)
    unaries = np.dstack([wl_mat,-wl_mat]).astype(np.int32)
    pairwise = -0 * np.eye(2, dtype=np.int32)
    result = cut_simple(unaries, pairwise)
    print unaries
    print result
    plt.subplot(235, title="cut_simple")
    plt.imshow(result, interpolation='nearest')
    sys.exit()
    '''
    
    '''
    "n_data_for_AR" indicates the number of data to fit AR model.
    By using fitted model, next "n_forecasted" data is/are estimated.
    Large "n_forecasted" does not make sense(approximately same as Linear regression.
    '''
    n_data_for_AR = 19
    n_forecasted = 1
    
    if wl_mat.shape[1]-n_data_for_AR-n_forecasted < 0:
        print "Number of Data for AR must be smaller than number of entire data."
        sys.exit()
    elif n_data_for_AR ==0 or  n_forecasted ==0:
        print "Data for AR is not given."
        sys.exit()
        
    Likelihood_mat = np.empty((wl_mat.shape[0],wl_mat.shape[1]-n_data_for_AR-n_forecasted+1), dtype=np.float)
    
    wl_mat = np.rint(wl_mat)
    for j in range(wl_mat.shape[0]):
        wl = wl_mat[j]
        for i in range(0,len(wl)-n_data_for_AR-n_forecasted):
            # Extract data for AR from entire workload data and input it to the function
            #y= getLikelihood(wl[i:i+n_data_for_AR+n_forecasted-1],np.zeros(len(wl)),order=[1,1,2])
            print wl
            print "**************", i , j, "**************************" 
            Likelihood_mat[j][i] = getLikelihood(wl[i:i+n_data_for_AR+n_forecasted-1],np.zeros(len(wl)))
    
    np.save('likelihood.npy', Likelihood_mat)
    for i in Likelihood_mat:
        for j in i:
            print j,
        print 
    Likelihood_mat = Likelihood_mat*10
    Likelihood_mat = Likelihood_mat.astype(int)
    print Likelihood_mat
    
    
    #wl_mat = wl_mat.astype(int)
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
   
    
    X = X[:100]
    y = y[:100]
    
    
    #Add edges
    for i in range(X.shape[0]):
        X[i] = [X[i], np.vstack([(0,1),(2,2)])]
        
    model = GraphCRF(directed=True, inference_method="max-product")
    
    X_train, X_test, y_train, y_test = sklearn.cross_validation.train_test_split(X,y, test_size =0.5, random_state=0)
    ssvm = FrankWolfeSSVM(model=model, C=.1, max_iter=10)
    ssvm.fit(X_train,y_train)
    print ssvm.score(X_test, y_test)
    print ssvm.predict(X_test)
    print y_test
    
    '''
    for i in range(X.shape[0]):
        
        X_train, X_test = X[] 
        X_test = X[i]
        y_test = y[i]
        X_train = np.delete(X,i)
        y_train = np.delete(y,i)
        
    
        ssvm = FrankWolfeSSVM(model=model, C=.1, max_iter=10)
        ssvm.fit(X_train,y_train)
        print ssvm.model
        print X_test[1].shape
        print ssvm.score(X_test, y_test)
        print y_test
    
        sys.exit()
    '''
    
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
    
    
    
