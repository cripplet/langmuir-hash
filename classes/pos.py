# classical (x, y) position vectors
class Pos:
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def __add__(self, other):
		return(Pos(self.x + other.x, self.y + other.y))

	def __eq__(self, other):
		return(
			(self.x == other.x) and
			(self.y == other.y))

	def __mul__(self, factor):
		return(Pos(factor * self.x, factor * self.y))

	def __ne__(self, other):
		return(not(self == other))

	def __str__(self):
		return("(" + str(self.x) + ", " + str(self.y) + ")")

	def __sub__(self, subtrahend):
		return(self + (subtrahend * -1))
