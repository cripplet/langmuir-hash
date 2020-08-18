#!/usr/bin/python

# custom libs
from classes.experiment import Experiment
from classes.frame import Frame
from lib.args import getArgs, getConf
from lib.debg import debug
from lib.misc import genFrame, initDir, renderConfig, renderCSV

# Python libs
from time import gmtime, strftime, time
from os import listdir
from os.path import dirname

def main(stamp):
	# gets a list of command line arguments
	args = getArgs()
	if(args["mode"] == "sim"):
		sim(args["conf"], args["grid"], stamp)
	elif(args["mode"] == "ren"):
		ren(args["conf"], args["grid"])
	elif(args["mode"] == "lyz"):
		lyz(args["conf"], args["grid"])
	elif(args["mode"] == "log"):
		log(args["dir"])

def sim(confFile, gridFile, stamp):
	conf = getConf(confFile)
	if(conf["name"] != ""):
		conf["name"] = "." + conf["name"]
	conf["fold"] = initDir("logs/" + stamp + conf["name"])
	expr = Experiment(conf["steps"], conf["logs"], conf["hori"], conf["diag"], conf["dens"], conf["beta"], conf["energies"], gridFile, conf["mail"], conf["fold"], conf["name"])
	expr.run()

def ren(confFile, gridFile):
	print(genFrame(gridFile).renderGrid("cur", False))
	# computs the total energy of the grid
	if(confFile != ""):
		conf = getConf(confFile)
		expr = Experiment(conf["steps"], conf["logs"], conf["hori"], conf["diag"], conf["dens"], conf["beta"], conf["energies"], gridFile, conf["mail"], "", conf["name"])
		expr.setEnergies()
		print(renderConfig(confFile))
		print("total energy: " + str(expr.frame.getFrameEnergy(expr, "cur")))


def log(dir):
	s = "name,steps,dens,hori,diag,beta,000000,000001,000011,000101,001001,000111,001011,010011,010101,001111,010111,011011,011111,111111\n"
	for log in listdir(dir):
		s += renderCSV(dir + log) + "\n"
	print(s)

def lyz(confFile, gridFile):
	conf = getConf(confFile)
	expr = Experiment(conf["steps"], conf["logs"], conf["hori"], conf["diag"], conf["dens"], conf["beta"], conf["energies"], gridFile, conf["mail"], "", conf["name"])
	print(expr.renderAnalysis(expr.getAnalysis(conf["energies"])))

# profiling modules
# http://bit.ly/bpSw41, http://bit.ly/GY61Vj, http://bit.ly/2g5rBr
# import cProfile
# import pstats

# stamp = strftime("%Y.%m.%d.%H.%M")

# filename = 'prof/' + str(int(time() * 1000000)) + '.prof'
# cProfile.run('main(stamp)', filename)

# prof = pstats.Stats(filename)
# prof.sort_stats('cumulative').print_stats(10)

# running the program
main(strftime("%Y.%m.%d.%H.%M"))
