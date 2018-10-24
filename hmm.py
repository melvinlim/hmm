def array(n,xi=0):
	return [xi for _ in xrange(n)]
def matrix(m,n,xi=0):
	return [[xi for _ in xrange(n)] for _ in xrange(m)]
class HMM:
	def __init__(self,STATES,SYMBOLS,OBSERVATIONS):
		self.N=STATES
		self.M=SYMBOLS
		self.T=OBSERVATIONS
		N=self.N
		M=self.M
		T=self.T
		self.A=matrix(N,N)
		self.B=matrix(N,M)
		tmp=1.0/N
		self.pi=array(N,tmp)
		self.alpha=matrix(T,N)
	def forward(self,obs):
		for i in xrange(self.N):
			self.alpha[1][i]=self.pi[i]*self.B[i][obs[1]]
		for t in xrange(self.T-1):
			tmp=0
			for j in xrange(self.N):
				for i in xrange(self.N):
					tmp+=self.alpha[t][i]*self.B[j][obs[t+1]]
			self.alpha[t+1][j]=tmp
