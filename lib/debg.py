# Python libs
from sys import exit
from time import localtime, strftime
def debug(s):
	msg("debug", s)

def error(s):
	msg("error", s)

def msg(header, s):
	print(header + ": " + str(s))

def panic(s):
	error(s)
	exit(1)

def status(s):
	status = strftime("(%H:%M:%S %Z, %m.%d.%Y) ", localtime())
	msg(status, s)

# bin(i) format is 0bxxxxxx - first [2:] strips '0b', and second [-width:] selects last < width > chars
# str.zfill(width) pads left side with zeros
def toBin(i, width = 6):
	return(bin(i)[2:][-width:].zfill(width))
