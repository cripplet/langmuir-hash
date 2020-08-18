# custom libs
from classes.particle import Particle
from classes.frame import Frame
from lib.debg import debug, panic, status
from lib.misc import genFrame, genPermutations, pad, renderConfig, resolveBoundary, toBin

# Python libs
from copy import deepcopy
from getpass import getuser
from math import exp
from random import random
from socket import gethostname
from subprocess import Popen
from time import localtime, strftime

# note:
#	"x" refers to DIAGONAL dimension and "y" the HORIZONTAL dimension within the code
#	this is due to Python arrays using the classic (row, col) notation
#	this is purely for notational purposes - .renderGrid() corrects for this by transposing array
class Experiment:
	def __init__(self, steps, logs, hori, diag, dens, beta, energies, grid, mail, directory, name):
		# how many logs to take
		self.logs = logs
		# the shortname of the simulation
		self.name = name
		# make directory to store logs
		self.directory = directory
		# .steps: number of equilibrium iterations to run
		self.steps = steps
		self.hori = hori
		self.diag = diag
		# .dens: there must be at least one free particle to move
		self.dens = min([.99, dens])
		self.beta = beta
		self.mail = mail
		self.n = int(round(self.hori * self.diag * self.dens))
		if(grid != ""):
			self.frame = genFrame(grid)
		else:
			self.frame = Frame(self.hori, self.diag, self.n, list(grid))
		# make sure grid is valid
		self.frame.checkFrame(self.hori, self.diag, self.n)
		self.energies = energies
		self.logStepSize = int(self.steps / self.logs)
		self.mailStepSize = int(self.steps / 2)

	# run the Boltzmann computation
	# returns a bool
	def accept(self, curEnergy, tmpEnergy):
		if(tmpEnergy < curEnergy):
			return(True)
		# setting overflow at e^(100 * .beta)
		deltaEnergy = tmpEnergy - curEnergy
		if(exp(min(deltaEnergy, 100) * self.beta) > random()):
			return(True)
		return(False)

	# makes sure that the energy delta being calculated is accurate
	# invoked in .accept()
	# note: this is a debugging feature - do not use when running a non-testing simulation
	# note:
	#	this provides motivation for not invoking (particle).resetParticle() in .frame.update()
	#	.checkEnergy() does not invoke panic() even when (particle).resetParticle() is not called
	def checkEnergy(self, deltaEnergy):
		curEnergy = self.frame.getFrameEnergy(self, "cur")
		tmpEnergy = self.frame.getFrameEnergy(self, "tmp")
		if(tmpEnergy - curEnergy != deltaEnergy):
			panic("energy deltas do not agree (accept())")

	# tests to see if .grid has particle at pos (x, y)
	# returns a particle with (particle).fill oneof (True, False)
	def find(self, x, y, key):
		index = self.frame.grid[key][x][y]
		if(index < 0):
			return(Particle(key, index, False, x, y))
		return(self.frame.particles[key][index])

	# ratio of particles in x configuration
	# note: costly function - should only be called at the end of the simulation
	def getAnalysis(self, initEnergies):
		analysis = dict()
		for energyDict in initEnergies:
			for config in energyDict:
				analysis[config] = 0
		# count the number of particles in each configuration
		for particle in self.frame.particles["cur"]:
			particle.getNeighbors(self)
			permutations = genPermutations(particle.getConfiguration(), 6)
			for config in analysis:
				if(int(config, 2) in permutations):
					analysis[config] += 1
					break
		# normalize the dict values
		for config in analysis:
			analysis[config] = 100 * (float(analysis[config]) / float(self.n))
		return(analysis)

	# picks a random particle within the grid that is not completely surrounded by other particles
	def getCurParticle(self):
		while True:
			particle = self.frame.particles["cur"][int(random() * self.n)]
			particle.getNeighbors(self)
			particle.getCount()
			if(particle.count < 6):
				return(particle)

	# returns the corresponding particle from .frame.particles["tmp"] as the given index
	def getTmpParticle(self, index):
		tmpParticle = self.frame.particles["tmp"][index]
		tmpParticle.getNeighbors(self)
		return(tmpParticle)

	def logAnalysis(self, analysis):
		fp = open(self.directory + "/analysis.txt", "w")
		fp.write(self.renderAnalysis(analysis))
		fp.close()

	# log experimental constants
	def logConstants(self):
		fp = open(self.directory + "/config.conf", "w")
		fp.write(self.renderConstants())
		fp.close()

	# logs the current frame as a seperate text file for future use
	def logStep(self, step):
		strStep = pad(step + 1, self.steps)
		fp = open(self.directory + "/" + strStep + ".txt", "w")
		fp.write(self.frame.renderGrid("cur", True))
		fp.close()

	# moves tmp particle to a random, empty adjacent location
	def moveTmpParticle(self, tmpParticle):
		tmpNeighborPositions = list()
		for loc in tmpParticle.neighbors:
			if(not(tmpParticle.neighbors[loc].isParticle())):
				tmpNeighborPositions.append(tmpParticle.neighbors[loc].pos)
		if(not(tmpNeighborPositions)):
			panic("returned an immobile particle (moveTmpParticle())")
		position = tmpNeighborPositions[int(random() * len(tmpNeighborPositions))]
		self.frame.update(self, tmpParticle, position)

	# email the experiment head on the simulation status
	# http://bit.ly/H3BRS1
	def notify(self, s):
		status(s)
		addr = getuser() + "@" + gethostname()
		s = strftime("%H:%M:%S %Z, %m.%d.%Y", localtime()) + "\r\n" + addr + " : " + self.directory + "\r\n\r\n" + renderConfig(self.directory + "/config.conf") + "\r\n" + s
		if(self.mail != ""):
			subject = self.directory + " (" + addr + ") simulation status update"
			Popen('echo "' + s + '" | mail -s "' + subject + '" "' + self.mail + '"', shell = True)

	def renderAnalysis(self, analysis):
		s = ""
		for config in analysis:
			# "%.2f" % (float) is a truncating operator (http://bit.ly/48LJv)
			ratio = "%.2f" % analysis[config]
			s += config + ": " + ratio + "%\n"
		return(s)

	# returns a formatted string of experimental constants
	def renderConstants(self):
		s = "steps: " + str(self.steps) + "\n"
		s += "logs: " + str(self.logs) + "\n"
		s += "name: " + str(self.name) + "\n"
		s += "mail: " + str(self.mail) + "\n"
		s += "hori: " + str(self.hori) + "\n"
		s += "diag: " + str(self.diag) + "\n"
		s += "dens: " + str(self.dens) + "\n"
		s += "beta: " + str(self.beta) + "\n"
		for energyDict in self.energies:
			for config in energyDict:
				s += config + ": " + str(energyDict[config]) + "\n"
		return(s)

	# returns current completion status
	def renderStatus(self, step):
		renderString = "step " + str(step + 1) + " / " + str(self.steps) + " (" + str(float(step + 1) / float(self.steps) * 100) + "%)"
		return(renderString)

	# periodic y boundary
	def resolveDiagBoundary(self, y):
		return(resolveBoundary(self.diag, y))

	# periodic x boundary
	def resolveHoriBoundary(self, x):
		return(resolveBoundary(self.hori, x))

	# in the simulation, run over .steps
	def run(self):
		self.logConstants()
		self.logStep(-1)
		initEnergies = deepcopy(self.energies)
		# pre-computes all possible energy configurations
		self.setEnergies()
		self.notify("starting simulation in " + self.directory)
		# xrange() constructs step as needed, vs. range() which constructs the list to be iterated over all at once
		# range() tends to hog memory when .steps is too high
		# http://bit.ly/mgDKG6
		for step in xrange(self.steps):
			# save move
			if(not((step + 1) % self.logStepSize)):
				status("\n" + self.frame.renderGrid("cur", False))
				self.logStep(step)
			# email move
			if(not((step + 1) % self.mailStepSize)):
				self.notify(self.renderStatus(step))
			self.step(step)
		self.logStep(self.steps - 1)
		analysis = self.getAnalysis(initEnergies)
		self.logAnalysis(analysis)
		self.notify("\r\nanalysis for " + self.directory + ":\r\n\r\n" + self.renderAnalysis(analysis))
		self.notify("simulation complete")

	# pre-generates all possible energy configurations
	# saves time in (particle).getEnergy()
	def setEnergies(self):
		for energyDict in self.energies:
			for config in energyDict.keys():
				for permutation in genPermutations(int(config, 2), len(config)):
					energyDict[permutation] = energyDict[config]
				del(energyDict[config])

	# each step consists of
	#	pick cur particle (.getCurParticle())
	#	pick tmp particle (.getTmpParticle())
	#	move tmp particle to random loc (.moveTmpParticle())
	#	calc old, new energies (.sumEnergy())
	#	run Boltzmann calc (.accept())
	#	accept / deny state (.frame.merge())
	def step(self, step):
		curParticle = self.getCurParticle()

		tmpParticle = self.getTmpParticle(curParticle.index)
		self.moveTmpParticle(tmpParticle)

		tmpParticle.getNeighbors(self)

		curIndices = curParticle.getNeighborIndices()
		tmpIndices = tmpParticle.getNeighborIndices()

		uniIndices = list(set(curIndices + tmpIndices))

		# calculates correct energies
		curEnergy = self.sumEnergy(uniIndices, "cur")
		tmpEnergy = self.sumEnergy(uniIndices, "tmp")

		# depreciated energy calculation model - use only for testing purposes
#		curEnergy = self.sumEnergy(curIndices, "cur")
#		tmpEnergy = self.sumEnergy(tmpIndices, "tmp")

		self.frame.merge(self.accept(curEnergy, tmpEnergy), self, curParticle, tmpParticle)

	# given a list of indices, find the total energy of the particles with indices
	def sumEnergy(self, indices, state):
		sum = 0
		for index in indices:
			self.frame.particles[state][index].getNeighbors(self)
			sum += self.frame.particles[state][index].getEnergy(self.energies)
		return(sum)
