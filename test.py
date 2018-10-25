import random
import sys
import hmm
import myprint
UPDATES=500
TRIALS=5
STATES=3
SYMBOLS=3
OBSERVATIONS=100
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
		self.previousIndex=-1
	def put(self,x):
		self.list.append(x)
		self.n+=1
	def draw(self):
		if self.n==0:
			return
		if self.previousIndex==0:
			index=random.randint(0,self.n-2)
		else:
			index=random.randint(0,self.n-1)
		self.previousIndex=index
		return self.list[index].draw()
def main(argv):
	predictions=[]
	probabilities=[]
	for trial in xrange(TRIALS):
		model=hmm.HMM(STATES,SYMBOLS,OBSERVATIONS)
		jars=Jars()
		jars.put(Jar([0,0,0,0,0,0,0,0,0,1,1,0,0,0,2]))
		jars.put(Jar([0,1,1,1,1,0,2,2]))
		jars.put(Jar([0,2,2,2,1,2]))
		obs=[]
		for i in xrange(OBSERVATIONS):
			obs.append(jars.draw())
		#model.info()
		for t in xrange(UPDATES):
			model.forward(obs)
			model.backward(obs)
			model.viterbi(obs)
			model.update(obs)
		predicted=model.info()
		predictions.append(predicted)
		pSymb=[]
		for i in xrange(SYMBOLS):
			pSymb.append(0.0)
		total=0
		for o in obs:
			pSymb[o]+=1.0
			total+=1.0
		for t in xrange(SYMBOLS):
			pSymb[t]/=total
		print 'actual pSymb',
		print pSymb
		probabilities.append(pSymb)
		print 'obs:',
		print obs
	print 'pred:',
	myprint.pprint(predictions)
	print 'prob:',
	myprint.pprint(probabilities)
	absError=0
	for t in xrange(TRIALS):
		for s in xrange(SYMBOLS):
			absError+=abs(predictions[t][s]-probabilities[t][s])
	print 'absError:',absError*1.0/TRIALS
if __name__=='__main__':
	main(sys.argv)
