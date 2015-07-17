'''
Created on 2015/07/14

@author: samejima
'''

import pandas as pd
from statsmodels.sandbox.gam import Offset
import matplotlib.pyplot as plt
pd.set_option('display.max_rows', 1000)
import statsmodels.api as sm
from pandas.tseries import offsets

import maxflow
from maxflow import fastmin



# Use only the 0th column
df = pd.read_csv('../data/data.csv', usecols=[0])
#df.index = pd.date_range('2012-01-01', periods=1287, freq=offsets.Hour(3))
df.index = pd.date_range('2010-01-01 12:00:00', periods=1287, freq=offsets.Minute(5))
dfms = df[df.index <= '2010-01-03']
print df

# ARMA(p, q) means 
# phi*y_t-1...+ phi*y_t-p + e_t - theta_1*e_t-1-...theta_q * e_t-q

# ARMA with p=11, q=0
arma_mod11 = sm.tsa.ARMA(dfms, (3,0)).fit()
result = arma_mod11.predict("2010-01-02", "2010-01-04", dynamic=True)
print result
print result.params