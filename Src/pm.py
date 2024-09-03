import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math


def plate(T0,T1,h,kappa,iter):
    
    # Setting conversion of parameters
    T0K = T0 + 273
    T1K = T1 + 273
    hm = h*1000
    k = kappa*1e-6
    Myty = 1e6*365*24*60*60
    t = 300*Myty

    #numerics
    nx = 300
    ny = h+1
    y = np.linspace(0,hm,ny)
    x = np.linspace(1*Myty,t,nx)
    X,Y = np.meshgrid(x, y,indexing='ij')
    
    T = np.zeros((nx,ny))
    it = T
    erf_vect = np.vectorize(math.erf)
    #calculation
    
    for i in range(1,iter+1):
        it = it + 1/i*np.exp(-(k*i**2*np.pi**2*X)/hm**2)*np.sin(i*np.pi*Y/hm)
        
    T = T0K + (T1K-T0K)*(Y/hm + 2/np.pi*it)
    return (x/Myty, y/1000, T-273)    
    

#XX,YY,TT = half()
#fig,ax = plt.subplots()
#im=ax.contourf(XX,YY,TT)
#ax.invert_yaxis()
#fig.colorbar(im)
#plt.show()