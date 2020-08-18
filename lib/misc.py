# custom libs
from lib.args import getConf

# Python libs
from re import sub
from os import mkdir
from os.path import exists
from getpass import getuser
from socket import gethostname

def genFrame(file):
	from classes.frame import Frame
	from lib.array import getGrid
	grid = getGrid(file)
	return(Frame(len(grid[0]), len(grid), 0, grid))

# given an int (treated as binary list), generate all unique rotational permutations of int (circular shifts)
# http://bit.ly/GLdKmI
def genPermutations(i, width):
	permutations = list()
	for j in range(width):
		permutations.append(i)
		# (i & 1) << (width - 1) advances the end bit to the beginning of the binary string
		i = (i >> 1) | ((i & 1) << (width - 1))
	return(list(set(permutations)))

# given a string representation of a neighbor configuration, return the number of neighbors in the configuration
def getConfigNum(config):
	return(len(filter(lambda x: x == "1", list(config))))

# makes a unique directory
def initDir(dir):
	i = 0
	tmpDir = dir
	while(exists(tmpDir)):
		i += 1
		tmpDir = dir + "." + str(i)
	mkdir(tmpDir)
	return(tmpDir)

def pad(i, max):
	maxLength = len(str(max))
	return(str(i).zfill(maxLength))

def resolveBoundary(bound, coord):
	if(coord < 0):
		return(coord + bound)
	if(coord > bound - 1):
		return(coord - bound)
	return(coord)

# given an array of lines:
#	stripping lines that begin with "#"
#	stripping the rest of a line with "#" in the middle
#	stripping lines that end with ":"
#	remove whitespace
def prep(file):
	lines = list()
	for line in file:
		line = sub(r'\s', '', line.split("#")[0])
		if((line != "") and (line[-1] != ":")):
			lines.append(line)
	return(lines)

# bin() format is "0bxxxxxx"
#	[2:] strips "0b"
#	[-width:] selects last < width > chars
def toBin(i, width):
	return(bin(i)[2:][-width:].zfill(width))

# renders the configuration file
# def renderConfig(folder):
#	if(folder[-1] != "/"):
#		folder += "/"
#	fp = open(folder + "config.conf", "r")
#	s = "config file for " + folder[:-1] + ":\n\n"
#	for line in fp:
#		s += line
#	return(s)

def renderConfig(name):
	fp = open(name, "r")
	s = "config file for " + name + ":\n\n"
	for line in fp:
		s += line
	return(s)

# given a config file, output a CSV line
def renderCSV(simulation):
	try:
		open(simulation + "/conf.conf", "r")
	except IOError as err:
		return()
	params = getConf(simulation + "/config.conf")
	s = getuser() + "@" + gethostname() + ":" + simulation + ","
	s += str(params["steps"]) + ","
	s += str(params["dens"]) + ","
	s += str(params["hori"]) + ","
	s += str(params["diag"]) + ","
	s += str(params["beta"]) + ","
	s += str(params["energies"][0]["000000"]) + ","
	s += str(params["energies"][1]["000001"]) + ","
	s += str(params["energies"][2]["000011"]) + ","
	s += str(params["energies"][2]["000101"]) + ","
	s += str(params["energies"][2]["001001"]) + ","
	s += str(params["energies"][3]["000111"]) + ","
	s += str(params["energies"][3]["001011"]) + ","
	s += str(params["energies"][3]["010011"]) + ","
	s += str(params["energies"][3]["010101"]) + ","
	s += str(params["energies"][4]["001111"]) + ","
	s += str(params["energies"][4]["010111"]) + ","
	s += str(params["energies"][4]["011011"]) + ","
	s += str(params["energies"][5]["011111"]) + ","
	s += str(params["energies"][6]["111111"])
	return(s)
