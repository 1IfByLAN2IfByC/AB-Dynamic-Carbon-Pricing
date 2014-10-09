# function that controls solving the demand function

import sympy as sym
from numpy import *

def equilibrium(demandElast, supplyElast, population, quantS):
	''' program that finds the equilibrium price given the elasticities 
		of supply and demand, as well as the population and quantity supplied

		will solve for the equilibrium price as well as the market price 
		assuming that all goods are dumped onto the market at the 
		beginning of the period'''

	def demandfun(demandAbs, elasticity):

		# of form:
		# demand = demand_(t-1) * (1+growth)

		demand, Q = sym.symbols('demand Q')
			
		demand = demandAbs  - (elasticity)*Q 
			
		return demand 
		
	def supplyfun(elasticity):

		supply, Q = sym.symbols('supply Q')
		intercept = 0 

		supply = elasticity*Q + intercept
			
		return supply

	supply = supplyfun(supplyElast)
	demand = demandfun(population, demandElast) 

	Q = sym.symbols('Q')

	# eqQ = sym.solve(supply - demand, Q) 
	# eqP = supply(eqQ) 

	marketP = demand.evalf(subs={Q: quantS})

	return marketP