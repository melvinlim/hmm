import random
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
		self.list.append(Jar(x))
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
