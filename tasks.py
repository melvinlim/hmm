import jars
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
