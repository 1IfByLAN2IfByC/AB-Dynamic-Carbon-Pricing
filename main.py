from numpy import *
import agent
import optimizeDone, equilibrium
from pprint import pprint 
import sympy as sym
import matplotlib.pylab as plt
import pdb 
reload(agent)
reload(optimizeDone)

numPlayers = 2 
numTurns = 10
numGenTypes = 3
deps = .1
population = 10
numIters = 100


Q = zeros((1, numTurns))

# agent = __(self, name, nuclear, gas, wind, utility, costs, damping, bank, permits=0.0):
# utility is given in the the form: array([revenue, utilization, emissions]) with sum(utility) = 1 
# costs are given in the form: array([gas, nuclear, wind])
suz = agent.Agent('Suz', 10, 3, 5, array([.2, .6, .2]), array([3.0, 4.0, 5.0]),  1, 0, numTurns)
michael = agent.Agent('Michael', 10, 5, 12, array([.6, .3, .1]), array([2.8, 4.2, 10.0]), .7, 0, numTurns)

agents = [suz, michael]
supply, utilization= agent.optimizationMatrix(michael, suz)

for k in xrange(0, numTurns):
	print 'Begin turn %s' % k
	production = zeros((1, numPlayers*numGenTypes))
	Q_actual = zeros((1, numPlayers*numGenTypes))

	## cycle through each player and see what their production is
	# optimize(Agent, matrixIN, utilizationMatrix, population, numPlayers, maxIter):
	i = 0
	for A in agents:
		production, utility = optimizeDone.optimize(A, supply, utilization, population, numPlayers, numIters)
		# A.production[k, :] = production[i*3: (i*numGenTypes)+3 ]*A.damping[-1]
		A.production[k, :] = production[i*3: (i*numGenTypes)+3 ]*A.damping[-1]

		A.utility = append(A.utility, utility)
		Q_actual[0, i*3 : (i*numGenTypes)+3] = A.production[k, :]
		# print sum(production)
		A.production_expected = append(A.production_expected, sum(production))

		i = i + 1

	## calculate actual aggragate supply and CO2 levels
	Q_actual = sum(Q_actual)

	# find market price at actual supply and see profits
	demand = equilibrium.demandfun(population, deps)
	q = sym.symbols('Q')
	P_actual = demand.evalf(subs={q:Q_actual})

	Q[0, k] = Q_actual


	pdb.set_trace()
	for A in agents:
		A.bank = A.bank + sum(A.production*P_actual - A.production-A.costs)
		# print (Q_actual - A.production_expected[-1])
		A.delta = append(A.delta, (-Q_actual + A.damping[-1]*A.production_expected[-1]))

		A.dampingUpdate()


for A in agents:
	pprint (vars(A))
	print '\n'


t = arange(0, numTurns)
T = arange(0, numTurns+1)
plt.subplot(3,1,1)
plt.plot(t, michael.delta, label='Michael delta')
plt.plot(t, suz.delta, label='Suz delta')
plt.legend()
plt.subplot(3,1,2)
plt.plot(T, michael.damping, label = 'Michael damping')
plt.plot(T, suz.damping, label='Suz damping')


plt.subplot(3,1,3)
plt.plot(t, sum(michael.production, 1), label='Michael Production')
plt.plot(t, Q.transpose(), label='Total Production')
plt.plot(t, michael.production_expected*michael.damping[0:-1], label='Michael mod. expecations')

plt.legend()

plt.show()



