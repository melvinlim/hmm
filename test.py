import random
import sys
import hmm
TRIALS=5
STATES=3
SYMBOLS=3
OBSERVATIONS=40
class Jar:
	def __init__(self,l=[]):
		self.list=l
		self.n=len(l)
	def put(self,x,n=1):
		for i in range(n):
			self.list.append(x)
		self.n+=n
	def draw(self,replace=True):
		if self.n==0:
			return
		index=random.randint(0,self.n-1)
		if not replace:
			self.list.remove(index)
		return self.list[index]
class Jars:
	def __init__(self):
		self.list=[]
		self.n=0
	def put(self,x):
		self.list.append(x)
		self.n+=1
	def draw(self):
		if self.n==0:
			return
		index=random.randint(0,self.n-1)
		return self.list[index].draw()
def main(argv):
	model=hmm.HMM(STATES,SYMBOLS,OBSERVATIONS)
	jars=Jars()
	jars.put(Jar([0,1,1,2]))
	jars.put(Jar([0,1,2,2]))
	jars.put(Jar([0,2,2,2]))
	obs=[]
	for i in xrange(OBSERVATIONS):
		obs.append(jars.draw())
	print obs
	model.info()
	model.forward(obs)
	model.backward(obs)
	model.viterbi(obs)
	model.update(obs)
	model.info()
if __name__=='__main__':
	main(sys.argv)
