def pprinta(array):
	for element in array:
		print '\t%.3f'%element,
	print
def pprint(matrix):
	for row in matrix:
		for element in row:
			print '\t%.3f'%element,
		print
	print
def array(n,xi=0):
	return [xi for _ in xrange(n)]
def matrix(m,n,xi=0):
	return [[xi for _ in xrange(n)] for _ in xrange(m)]
def tensor(i,j,k,xi=0):
	return [[[xi for _ in xrange(k)] for _ in xrange(j)] for _ in xrange(i)]
class HMM:
	def __init__(self,STATES,SYMBOLS,OBSERVATIONS):
		self.N=STATES
		self.M=SYMBOLS
		self.T=OBSERVATIONS
		N=self.N
		M=self.M
		T=self.T
		self.A=matrix(N,N,0.1)
		self.B=matrix(N,M,0.1)
		tmp=1.0/N
		self.pi=array(N,tmp)
		self.alpha=matrix(T,N)
		self.beta=matrix(T,N)
		self.delta=matrix(T,N)
		self.psi=matrix(T,N)
		self.xi=tensor(T,N,N)
		self.gamma=matrix(T,N)
	def info(self):
		print 'pi =',
		pprinta(self.pi)
		print 'A =',
		pprint(self.A)
		print 'B =',
		pprint(self.B)
	def forward(self,obs):
		for i in xrange(self.N):
			self.alpha[0][i]=self.pi[i]*self.B[i][obs[0]]
		for t in xrange(self.T-1):
			tmp=0
			for j in xrange(self.N):
				for i in xrange(self.N):
					tmp+=self.alpha[t][i]*self.B[j][obs[t+1]]
				self.alpha[t+1][j]=tmp
	def backward(self,obs):
		for i in xrange(self.N):
			self.beta[self.T-1][i]=1
		for t in xrange(self.T-1-1,-1,-1):
			for i in xrange(self.N):
				tmp=0
				for j in xrange(self.N):
					tmp+=self.A[i][j]*self.B[j][obs[t+1]]*self.beta[t+1][j]
				self.beta[t][i]=tmp
	def viterbi(self,obs):
		for i in xrange(self.N):
			self.delta[0][i]=self.pi[i]*self.B[i][obs[0]]
			self.psi[0][i]=0
		for t in xrange(1,self.T):
			maxVal=0
			maxArg=0
			for j in xrange(self.N):
				for i in xrange(self.N):
					tmp=self.delta[t-1][i]*self.A[i][j]
					if tmp>maxVal:
						maxVal=tmp
						maxArg=i
				self.delta[t][j]=maxVal*self.B[j][obs[t]]
				self.psi[t][j]=maxArg
	def update(self,obs):
		N=self.N
		M=self.M
		T=self.T
		for t in xrange(T-1):
			tmp=0
			for i in xrange(N):
				for j in xrange(N):
					tmp+=self.alpha[t][i]*self.A[i][j]*self.B[j][obs[t+1]]*self.beta[t+1][j]
#			self.pObsGivenModel[t]=tmp
			normalizer=tmp
			for i in xrange(N):
				xij=0
				tmp=0
				for j in xrange(N):
					xij=self.alpha[t][i]*self.A[i][j]*self.B[j][obs[t+1]]*self.beta[t+1][j]/normalizer
					self.xi[t][i][j]=xij
					tmp+=xij
				self.gamma[t][i]=tmp
		for i in xrange(N):
			self.pi[i]=self.gamma[0][i]
		for i in xrange(N):
			for j in xrange(N):
				sumXi=0
				sumGamma=0
				for t in xrange(T-1):
					sumXi+=self.xi[t][i][j]
					sumGamma+=self.gamma[t][i]
				self.A[i][j]=sumXi/sumGamma
		for j in xrange(N):
			for k in xrange(M):
				gammaObsSymbVk=0
				sumGamma=0
				for t in xrange(T):
					sumGamma+=self.gamma[t][j]
					if obs[t]==k:
						gammaObsSymbVk+=self.gamma[t][j]
				self.B[j][k]=gammaObsSymbVk/sumGamma
