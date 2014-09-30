# function that handles supply curve 
# inputs:
#	expectations
#	previous supply

import sympy as sym
from numpy import *

def supplyfun(elasticity):

	supply, Q = sym.symbols('supply Q')
	intercept = 0 

	supply = elasticity*Q + intercept
		
	return supply
		
		
