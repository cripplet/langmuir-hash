# custom libs
from classes.pos import Pos
from lib.debg import panic
from lib.misc import toBin

class Particle:
	def __init__(self, state, index, fill, x, y):
		self.state = state
		self.index = index
		# a particle is either empty or filled
		# fill == False only used in the case of finding neighbors
		self.fill = fill
		self.pos = Pos(x, y)
		self.neighbors = dict()
		self.count = 0
		self.configuration = 0

	def __eq__(self, other):
		return(
			(self.state == other.state) and
			(self.index == other.index) and
			(self.fill == other.fill) and
			(self.pos == other.pos))

	def __str__(self):
		if(self.isParticle()):
			state = "filled"
		else:
			state = "empty"
		return(state + " particle at " + str(self.pos) + " in " + self.state + " state")

	# configurations are represented as binary strings starting counterclockwise from lTop
	#   0 1
	# 0	1
	#   0 0
	# this configuration maps to 000011 (int(.configuration) == 3)
	def getConfiguration(self):
		self.getCount()
		self.configuration = 0
		orderDict = dict({
			"lTop" : 32,
			"lMid" : 16,
			"lBot" : 8,
			"rBot" : 4,
			"rMid" : 2,
			"rTop" : 1})
		for loc in orderDict:
			if(self.neighbors[loc].isParticle()):
				self.configuration += orderDict[loc]
		return(self.configuration)

	# get number of nonempty spaces around particle
	def getCount(self):
		self.count = 0
		if(self.neighbors == dict()):
			panic("no neighbors (getCount())")
		for key in self.neighbors:
			if(self.neighbors[key].isParticle()):
				self.count += 1
		return(self.count)

	# get the energy of the particle configuration
	def getEnergy(self, energies):
		if(self.neighbors == dict()):
			panic("no neighbors (getEnergy())")
		self.getConfiguration()
		energyDict = energies[self.count]
		if(self.configuration in energyDict):
			return(energyDict[self.configuration])
		panic("cannot find a possible permutation (getEnergy())")

	# returns a list of the indices of the particle and neighboring particles
	def getNeighborIndices(self):
		indices = list([self.index])
		for loc in self.neighbors:
			if(self.neighbors[loc].isParticle()):
				indices.append(self.neighbors[loc].index)
		return(indices)

	# given a particle, find the adjacent neighbors in a hexagonal lattice
	def getNeighbors(self, expr):
		self.neighbors = dict()
		posDict = dict({
			"hCoord" : self.pos.x,
			"dCoord" : self.pos.y,
			"lCoord" : expr.resolveHoriBoundary(self.pos.x - 1),
			"rCoord" : expr.resolveHoriBoundary(self.pos.x + 1),
			"tCoord" : expr.resolveDiagBoundary(self.pos.y + 1),
			"bCoord" : expr.resolveDiagBoundary(self.pos.y - 1)
		})
		self.neighbors = {
			"lTop" : expr.find(posDict["hCoord"], posDict["bCoord"], self.state),
			"lMid" : expr.find(posDict["lCoord"], posDict["dCoord"], self.state),
			"lBot" : expr.find(posDict["lCoord"], posDict["tCoord"], self.state),
			"rTop" : expr.find(posDict["rCoord"], posDict["bCoord"], self.state),
			"rMid" : expr.find(posDict["rCoord"], posDict["dCoord"], self.state),
			"rBot" : expr.find(posDict["hCoord"], posDict["tCoord"], self.state)
		}
		return(self.neighbors)

	def isParticle(self):
		return(self.fill)

	def move(self, pos):
		self.pos.x = pos.x
		self.pos.y = pos.y

	# returns .configuration in binary form
	def renderConfiguration(self):
		return(toBin(self.configuration, 6))

	# returns a list of neighbors and (iteration) level of surrounding neighbors
	# this is a very processor-intensive function - do not call on this when
	#	iterations > 0
	#	during non-testing simulations
	def renderNeighbors(self, experiment, iterations, indentation = 0):
		if(self.isParticle()):
			if(self.neighbors == dict()):
				panic("no neighbors (renderNeighbors())")
			renderString = "".rjust(indentation) + "neighbors of " + str(self) + "\n"
			for loc in self.neighbors:
				# rjust() indents each line
				renderString += "".rjust(indentation + 2) + "(" + loc + ") " + str(self.neighbors[loc]) + "\n"
				if(iterations and self.neighbors[loc].isParticle()):
					self.neighbors[loc].getNeighbors(experiment)
					renderString += self.neighbors[loc].renderNeighbors(experiment, iterations - 1, indentation + 2)
			return(renderString)

	# reset all information about neighbors and the neighboring configuration
	def resetNeighbors(self):
		self.count = 0
		self.configuration = 0
		self.neighbors = dict()

	# reset .neighbors and reset each .neighbors[loc].neighbors
	def resetParticle(self, expr, forced):
		if((self.neighbors == dict()) and forced):
			self.getNeighbors(expr)
		if(not(self.neighbors == dict())):
			for loc in self.neighbors:
				self.neighbors[loc].resetNeighbors()
		self.resetNeighbors()
