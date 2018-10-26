import jars
import random
import math
class Task:
	def __init__(self):
		x=1
class JarTask(Task):
	def __init__(self):
		self.jars=jars.Jars()
		self.jars.put([1,1,1,1,1,1,1,1,0,1,1,0,0,0,2])
		self.jars.put([0,1,1,1,1,0,2,2])
		self.jars.put([0,2,2,2,1,2])
	def draw(self):
		return self.jars.draw()
	def getNoisy(self,nObs,mean,var,trueObs,noisyObs):
		for o in xrange(nObs):
			trueObs.append(self.draw())
			noisyObs.append(self.draw()+self.noise(mean,var))
	def getSingleNoisy(self,mean,var,trueObs,noisyObs):
		trueObs.pop(0)
		noisyObs.pop(0)
		trueObs.append(self.draw())
		noisyObs.append(self.draw()+self.noise(mean,var))
	def noise(self,mean,var):
		if var==0:
			return 0
		x=random.randint(0,1000)/1000.0
		n=math.exp(-0.5*(x-0.5)**2/var)/(2*math.pi*var)
		return n-0.5
