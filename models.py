import random
class Model(object):
	def __init__(self):
		pass
	def train(self,obs):
		pass
	def info(self):
		pass
class UniformRandom(Model):
	def __init__(self,a,b):
		self.a=a
		self.b=b
	def predict(self):
		return (random.randint(self.a,self.b),0)
