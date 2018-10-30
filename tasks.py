import jars
import random
import math
import copy
class Task:
	def __init__(self):
		pass
class JarTask(Task):
	def __init__(self,POSITIVETASK=True):
		self.jars=jars.Jars()
		if POSITIVETASK:
			self.jars.put([+1,+1,+1,+1,+1,+1,+1,+1,0,+1,+1,0,0,0,+2])
			self.jars.put([0,+1,+1,+1,+1,0,+2,+2,3])
			self.jars.put([0,+2,+2,+2,+1,+2,4,4])
		else:
			self.jars.put([+1,+1,+1,+1,+1,+1,+1,+1,0,+1,+1,0,0,0,-1,2,2])
			self.jars.put([0,+1,+1,+1,+1,0,-1,-1])
			self.jars.put([0,-1,-1,-1,+1,-1,-2,-2])
	def draw(self):
		return self.jars.draw()
	def getNoisyTasks(self,maxObs,nTasks,mean,var,trueObsList,noisyObsList):
		trueObs=[]
		noisyObs=[]
		self.getNoisy(maxObs,mean,var,trueObs,noisyObs)
		trueObsList.append(trueObs)
		noisyObsList.append(noisyObs)
		for t in xrange(nTasks):
			trueObs=copy.deepcopy(trueObs)
			noisyObs=copy.deepcopy(noisyObs)
			self.getSingleNoisy(mean,var,trueObs,noisyObs)
			trueObsList.append(trueObs)
			noisyObsList.append(noisyObs)
	def getNoisy(self,nObs,mean,var,trueObs,noisyObs):
		for o in xrange(nObs):
			result=self.draw()
			trueObs.append(result)
			noisyObs.append(result+self.noise(var))
	def getSingleNoisy(self,mean,var,trueObs,noisyObs):
		trueObs.pop(0)
		noisyObs.pop(0)
		trueObs.append(self.draw())
		noisyObs.append(self.draw()+self.noise(var))
	def noise(self,var):
		if var==0:
			return 0
		x=random.randint(0,1000)/1000.0
		return x-0.5
