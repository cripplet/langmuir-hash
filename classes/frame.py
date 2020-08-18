# custom libs
from classes.particle import Particle
from lib.array import boolMap, initArray, shift
from lib.debg import debug, panic

# Python libs
from copy import deepcopy
from random import random

class Frame:
	def __init__(self, hori, diag, n, grid):
		self.grid = dict({
			"cur" : initArray(hori, diag, -1),
			"tmp" : initArray(hori, diag, -1)
		})
		self.particles = dict({
			"cur" : initArray(n, 1, False),
			"tmp" : initArray(n, 1, False)
		})
		if(grid == list()):
			self.rFill(hori, diag, n)
		else:
			self.cFill(hori, diag, grid)

	# initializes .grid and .particles with config'd grid
	# grid HAS been transposed (see .renderGrid())
	def cFill(self, hori, diag, grid):
		# untranspose grid
		grid = zip(*grid)
		# map grid back into indices
		i = 0
		for x in xrange(hori):
			for y in xrange(diag):
				if(grid[x][y] == "."):
					self.grid["cur"][x][y] = -1
				else:
					self.grid["cur"][x][y] = i
					self.particles["cur"].append(Particle("cur", i, True, x, y))
					self.particles["tmp"].append(Particle("tmp", i, True, x, y))
					i += 1
		self.grid["tmp"] = deepcopy(self.grid["cur"])

	# makes sure the frame is valid
	def checkFrame(self, hori, diag, n):
		# untranspose grid
		grid = zip(*self.grid["cur"])
		if(
			(len(grid[0]) != hori) or
			(len(grid) != diag) or
			(len(self.particles["cur"]) != n)):
			panic("frame dimensions do not match (checkFrame())")

	# debugging function - returns the total energy of a frame
	def getFrameEnergy(self, expr, state):
		totalEnergy = 0
		for particle in self.particles[state]:
			particle.getNeighbors(expr)
			totalEnergy += particle.getEnergy(expr.energies)
		return(totalEnergy)

	# initializes .grid and .particles randomly (new configuration)
	def rFill(self, hori, diag, n):
		# for each particle, randomly assign x and y positions
		for i in range(n):
			while True:
				x = int(random() * hori)
				y = int(random() * diag)
				if(self.grid["cur"][x][y] < 0):
					break
			self.grid["cur"][x][y] = i
			self.particles["cur"][i] = Particle("cur", i, True, x, y)
			self.particles["tmp"][i] = Particle("tmp", i, True, x, y)
		self.grid["tmp"] = deepcopy(self.grid["cur"])

	# merges the different states of .grid and .particles
	def merge(self, accepted, expr, curParticle, tmpParticle):
		if(accepted):
			self.update(expr, curParticle, tmpParticle.pos)
		else:
			self.update(expr, tmpParticle, curParticle.pos)

	# note:
	#	when rendering, transposing .grid[state] into "canonical" (x, y) coordinates
	#	any coordinates printed out can be accessed column-first, when viewed with rendered grid
	#	http://bit.ly/GHwkBf
	def renderGrid(self, state, toFile):
		from math import floor
		renderString = ""
		if(not(toFile)):
			i = 0
		grid = zip(*self.grid[state])
		for row in grid:
			if(toFile):
				tmpRow = map(lambda x: boolMap(x, ["X", "."]), row)
				renderString += "".join(tmpRow) + "\n"
			else:
				# int(floor(i / 2)) increments the shift value by one every two rows
				tmpRow = shift(map(lambda x: boolMap(x, ["X", " "]), row), int(floor(i / 2)))
				renderString += "[".rjust((i % 2) + 1) + " ".join(tmpRow) + "]" + "\n"
				i += 1
		return(renderString)

	# returns information on movement positions
	def renderMove(self, particle, position):
		return("moving " + str(particle) + " to " + str(position))

	# moves a particle to a given location
	# resets the neighbors at old and new locations
	# note:
	#	if an additional level of security is needed, (particle).resetParticle() can be invoked
	#	before and after (particle).move() to call (particle).resetNeighbors() on each neighbor of the particle
	#	for additional justification, see (experiment).checkEnergy()
	def update(self, experiment, particle, position):
		if(self.grid[particle.state][position.x][position.y] != -1):
			panic("target position is already occupied")
		particle.resetNeighbors()
		self.grid[particle.state][position.x][position.y] = particle.index
		self.grid[particle.state][particle.pos.x][particle.pos.y] = -1
		particle.move(position)
