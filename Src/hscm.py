import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math




def half(T0,T1,h,kappa):
    
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
    erf_vect = np.vectorize(math.erf)
    #calculation
    
    A_B = erf_vect(Y/(2*(k*X)**0.5))
    T = A_B*(T1K-T0K) + T0K
    return(x/Myty, y/1000,T-273)

#XX,YY,TT = half()
#fig,ax = plt.subplots()
#im=ax.contourf(XX,YY,TT)
#ax.invert_yaxis()
#fig.colorbar(im)
#plt.show()
