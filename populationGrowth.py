import numpy as np

def simDSLogistic(K,r,N0):
	'''intrinsic growth rate r, initial population size (inoculum) N0.  Returns an
	array with a (continuous) time column and a (discrete) population size column.'''
    # Unusually, for this model, we know the number of events a priori
	eventNo=K-N0
    # So we can just generate all required random numbers (quickly) in one go
	unifs=np.random.uniform(size=eventNo)
    # Every event produces one cell and consumes one unit of nutrients
	simres=np.zeros((eventNo+1,2),np.float)
	simres[:,1]=range(N0,K+1)
    # Simulate time between events by generating 
    # exponential random numbers using the inversion method
	dts=-np.log(1-unifs)/(r*simres[1:,1]*(1-simres[1:,1]/K))
	simres[1:,0]=np.cumsum(dts)
	return(simres)
