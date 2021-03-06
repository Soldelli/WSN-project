import numpy as np
from scipy import stats
import time as time
import matplotlib.pyplot as plt

def Robust_Soliton_Distribution(n, k, c0, delta):
    R = c0 * np.sqrt(k) * np.log(float(k)/delta)        # computation of R parameter
    d = np.zeros(n)                                     # initialization of degree variable

    #Tau Function
    tau = np.zeros(k)                                   # initialization of tau
    for i in range(1, k + 1):                           # computation of tau, it follows the formula on the papers
        if i <= round((k / R) - 1):
            tau[i - 1] = (float(R) / (i * k))
        elif i >= round((k / R) + 1):
            break
        else:                                           # case i == (k/R), since K/R is not integer equality is never matched
            tau[i - 1] = (float(R) * np.log(float(R) / delta)) / k  # verified, so ve use >= <= instead


    # Ideal Soliton Distribution
    sd = [1.0 / k]                                      # initialization of soliton distribution with first value
    [sd.append(1.0 / (j * (j - 1))) for j in range(2, k+1)] # append of other values following the formula in papers

    # Beta
    beta = np.sum([tau[i]+sd[i] for i in xrange(k)])    # computation of normalization parameter

    # Robust Soliton Distribution
    pdf = []                                            # initialization of target pdf
    for i in xrange(k):
        pdf.append((tau[i] + sd[i])/beta)               # computation of pdf using tau, sd and the normalization coeff


    xk = np.arange(1, k+1)                              # vector of degree, start from 1 and goes up to k
    custm = stats.rv_discrete(name='custm', values=(xk, pdf))   # creation of obj custm, see documentation

    for i in xrange(n):
        d[i] = custm.rvs()                              # randomly sample n elements from custm, following the
                                                        # distribution of custm
    return d,pdf, R                                     # return sampled degree



def Ideal_Soliton_Distribution(n, k, c0, delta):
    d = np.zeros(n)   # initialization of degree variable

    # Ideal Soliton Distribution
    sd = [1.0 / k]                                      # initialization of soliton distribution with first value
    [sd.append(1.0 / (j * (j - 1))) for j in range(2, k+1)] # append of other values following the formula in papers


    xk = np.arange(1, k+1)                              # vector of degree, start from 1 and goes up to k
    custm = stats.rv_discrete(name='custm', values=(xk, sd))   # creation of obj custm, see documentation
    for i in xrange(n):
        d[i] = custm.rvs()                              # randomly sample n elements from custm, following the
                                                        # distribution of custm
    return d, sd , R                                    # return sampled degree