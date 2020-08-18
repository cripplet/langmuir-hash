# parses command line for arguments
# http://bit.ly/x1b5DS

# custom libs
from lib.debg import error, panic
import lib.misc

# Python libs
from getopt import getopt, GetoptError
from sys import argv, exit

# m - either to render a grid, or to simulate
# c - the config file to read
# g - input grid
# d - the log directory
def getArgs():

	opts = "m:c:g:d:h"
	words = ["help"]
	args = dict({
		"dir" : "",
		"conf" : "",
		"grid" : "",
		"mode" : ""})

	# get command line arguments
	try:
		options, params = getopt(argv[1:], opts, words)
	except GetoptError, err:
		error(str(err))
		usage()
	# set environment variables
	for option, param in options:
		if(option in ("-h", "--help")):
			usage()
			exit(0)
		elif(option == "-m"):
			args["mode"] = str(param)
		elif(option == "-c"):
			args["conf"] = str(param)
		elif(option == "-g"):
			args["grid"] = str(param)
		elif(option == "-d"):
			param = str(param)
			if(param[-1] != "/"):
				param += "/"
			args["dir"] = param
	if(not(args["mode"] in ["sim", "ren", "lyz", "log"])):
		usage()
		exit(0)
	return(args)

# from a given configuration file, return a dictionary of experiment parameters
def getConf(file):
	conf = dict({
		"steps" : 10000,
		"logs" : 10,
		"name" : "",
		"hori" : 100,
		"diag" : 100,
		"dens" : 0.5,
		"beta" : -1.0,
		"mail" : "",
		"grid" : "",
		"energies" : list([
			{
				"000000" : 0},
 			{
				"000001" : 0},
			{
				"000011" : 0,
				"000101" : 0,
				"001001" : 0},
			{
				"000111" : 0,
				"001011" : 0,
				"010011" : 0,
				"010101" : 0},
			{
				"001111" : 0,
				"010111" : 0,
				"011011" : 0},
			{
				"011111" : 0},
			{
				"111111" : 0}])
		})
	fp = open(file, "r")
	tmpConf = lib.misc.prep(fp)
	# alter the configuration array with proper values
	for line in tmpConf:
		# split line into property and value
		key, val = line.split(":")
		if(key in list(set(conf.keys()) - set(["energies"]))):
			conf[key] = val
		elif(lib.misc.getConfigNum(key) == int(lib.misc.getConfigNum(key))):
			conf["energies"][lib.misc.getConfigNum(key)][key] = float(val)
		else:
			panic("illegal experiment constant (getConf())")
	return(typeCast(conf))

# ensures that the values in the configuration array are of the correct type
def typeCast(conf):
	conf["steps"] = int(conf["steps"])
	conf["logs"] = int(conf["logs"])
	conf["hori"] = int(conf["hori"])
	conf["diag"] = int(conf["diag"])
	conf["dens"] = float(conf["dens"])
	conf["beta"] = float(conf["beta"])
	return(conf)

# help message for this simulation
def usage():
	print("usage: " + argv[0] + " ( -h | --help\n\t\t| -m ( sim -c string [-g string]\n\t\t\t| ren [-c string] -g string\n\t\t\t| lyz -g string\n\t\t\t| log -d string ) )")
	print("\t-m(ode)\t: sim(ulate) OR ren(der) OR ana(lyz)e OR log")
	print("\t-c(onf)\t: read in a configuration file")
	print("\t-g(rid)\t: input grid (if invoked with -m ren, then read as starting grid configuration)")
	print("\t-d(ir)\t: input directory for logging mode")
	exit(0)
