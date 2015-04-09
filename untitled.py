from numpy import *

def utility(X, alpha, threshold):
	try:
		[m, n] = shape(X)
	except ValueError:
		m = len(X)
		n = 1

	# for each column in X, multiply by alpha 
	cost = zeros((m, 1))
	for i in xrange(0, m):

		## how to deal with NaN
		# find NaN
		NaN_list = isnan(X)

		# turn NaN's from rows into zeros
		X[NaN_list] = 0
		
		# redistribute NaN coeff. to other 
		coeffMissing = sum(alpha[NaN_list.reshape(len(NaN_list), 1)])
		alpha = alpha + (coeffMissing / len(NaN_list))

		# turn all other alpha into 0 
		alpha[NaN_list.reshape(len(NaN_list), 1)] = 0

		cost[m, 0] = dot(alpha, X.transpose())

	return cost

