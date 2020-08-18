# x refers to ROWS, y refers to COLUMNS (pre-render)

def boolMap(item, dict):
	if(item < 0):
		return(dict[1])
	return(dict[0])

# given a file, return a 2D (frame).grid["cur"]
def getGrid(file):
	grid = list()
	fp = open(file, "r")
	for line in fp:
		grid.append(list(line.rstrip("\n")))
	return(grid)

def initArray(x, y, val):
	return([[val for col in range(y)] for row in range(x)])

# shifts list n values to right
def shift(l, n):
	return(l[-n:] + l[:-n])
