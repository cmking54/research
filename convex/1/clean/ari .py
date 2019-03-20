import numpy as np

#def angle_between_vects(A,B):

def distance(A,B):
    return Math.sqrt(Math.pow(A[0]-B[0],2)+Math.pow(A[1]-B[1],2))

class Batch():
	#batch = None
	#filt = None
	#n = -1
	def __init__(self,limit,function):
		self.bound = limit
		self.comp = function
		self.batch = []

	def add(self,a):
		if len(self.batch) < self.bound:
			self.batch += [a]
		else:
			for i in range(self.bound):
				if self.comp(a,self.batch[i]):
					b = self.batch[i]
					self.batch[i] = a
					a = b

	def get(self,clear=False):
		l = self.batch
		if clear:
			self.batch = []
		return l

#example = Batch(5,lambda a,b: a <= b)
#for i in [5,3,8,4,2,7,4,2,4,36,5,6,7,5,3,5,6,88,9,7,5,43,2,1,34,23]:
	#example.add(i)
	#print example.get()
