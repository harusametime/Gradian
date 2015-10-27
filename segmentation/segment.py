#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 2015/07/14

@author: samejima
'''

import numpy as np
from scipy import stats
import pandas
import matplotlib.pyplot as plt
import statsmodels.api as sm


def GenData0():
    
    server1 =[]
    server2 =[]
    
    fp = open('../data/epa-http.txt', 'r')
    for line in fp.readlines():
        access = line.rstrip("\n").split("\t")
        server1.append(access[1])
    fp.close()
    
    fp = open('../data/sdsc_http.txt', 'r')
    for line in fp.readlines():
        access = line.rstrip("\n").split("\t")
        server2.append(access[1])
    fp.close()
    
    access_mat = np.array([server1,server2])
    print access_mat
    return access_mat
    
if __name__ == '__main__':
    access_mat = GenData0()