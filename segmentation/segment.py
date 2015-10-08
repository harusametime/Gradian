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
    wwwusage = sm.datasets.get_rdataset("WWWusage")
    print wwwusage.data