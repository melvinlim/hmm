import random
class Model(object):
	def __init__(self):
		self.name='Generic Model'
	def train(self,obs):
		pass
	def info(self):
		print self.name
class UniformRandom(Model):
	def __init__(self,a,b):
		self.a=a
		self.b=b
		self.name='Uniform Random Model'
	def predict(self):
		return (random.randint(self.a,self.b),0)
