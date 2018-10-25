import random
import myprint
import math
NOSCALEFACTOR=False
#NOSCALEFACTOR=True
PREVENTDIVIDEBYZERO=True
_1DGAUSS=True
_1DGAUSS=False
_KDGAUSS=False
def array(n,xi=0.0):
	return [xi for _ in xrange(n)]
def matrix(m,n,xi=0.0):
	return [[xi for _ in xrange(n)] for _ in xrange(m)]
def tensor(i,j,k,xi=0.0):
	return [[[xi for _ in xrange(k)] for _ in xrange(j)] for _ in xrange(i)]
def randomizeMatrix(mat):
	M=len(mat)
	N=len(mat[0])
	for i in xrange(M):
		for j in xrange(N):
			mat[i][j]=random.randint(5,100)/100.0
class Mixture:
	def __init__(self,mu,sigmaSq):
		self.mu=mu
		self.sigmaSq=sigmaSq
class HMM:
	def __init__(self,STATES,SYMBOLS,OBSERVATIONS):
		self.N=STATES
		self.M=SYMBOLS
		self.T=OBSERVATIONS
		N=self.N
		M=self.M
		T=self.T
		self.A=matrix(N,N,1.0/STATES)
		self.initB()
		self.pi=array(N,1.0/STATES)
		self.alpha=matrix(T,N)
		self.beta=matrix(T,N)
		self.alphaBar=matrix(T,N)
		self.betaBar=matrix(T,N)
		self.alphaHat=matrix(T,N)
		self.betaHat=matrix(T,N)
		self.delta=matrix(T,N)
		self.psi=matrix(T,N)
		self.xi=tensor(T,N,N)
		self.gamma=matrix(T,N)
		self.scalefactor=array(T,0)
		self.pObsGivenModel=array(T)
	def info(self):
		print 'pi =',
		myprint.pprinta(self.pi)
		print 'A =',
		myprint.pprint(self.A)
#		print 'B =',
#		myprint.pprint(self.B)
#		print 'alpha =',
#		myprint.pprint(self.alpha)
#		print 'beta =',
#		myprint.pprint(self.beta)
#		print 'delta =',
#		myprint.pprint(self.delta)
#		print 'psi =',
#		myprint.pprint(self.psi)
		if not NOSCALEFACTOR:
			print 'scalefactor =',
			myprint.pprinta(self.scalefactor)
		pSymb=array(self.M,0.0)
		for j in xrange(self.M):
			for i in xrange(self.N):
				#pSymb[j]+=self.B[i][j]
				pSymb[j]+=self.B(i,j)
		norm=sum(pSymb)
		if PREVENTDIVIDEBYZERO:
			if norm==0:
				norm=1
		for j in xrange(self.M):
			pSymb[j]/=norm
		print 'pSymb =',
		myprint.pprinta(pSymb)
		T=self.T
		tmp=self.delta[T-1][0]
		maxArg=0
		for i in xrange(1,self.N):
			if self.delta[T-1][i]>tmp:
				tmp=self.delta[T-1][i]
				maxArg=i
		t=T-1
		record=[]
		while t>=0:
#			print maxArg,
			record.append(maxArg)
			maxArg=self.psi[t][maxArg]
			t-=1
		record.reverse()
		print 'sta:',
		print record
		return pSymb
	def predict(self):
		T=self.T
		M=self.M
		tmp=self.delta[T-1][0]
		maxArg=0
		for i in xrange(1,self.N):
			if self.delta[T-1][i]>tmp:
				tmp=self.delta[T-1][i]
				maxArg=i
		state=maxArg
		tmp=self.B(state,0)
		maxArg=0
		for i in xrange(1,M):
			if self.B(state,i)>tmp:
				tmp=self.B(state,i)
				maxArg=i
		return maxArg,state
	def forward(self,obs):
		sumAlphaBar=0
		for i in xrange(self.N):
			self.alpha[0][i]=self.pi[i]*self.B(i,obs[0])
			self.alphaBar[0][i]=self.alpha[0][i]
			sumAlphaBar+=self.alphaBar[0][i]
		if sumAlphaBar>0.00000:
			self.scalefactor[0]=1.0/sumAlphaBar
		else:
			self.scalefactor[0]=1.0
		for i in xrange(self.N):
			self.alphaHat[0][i]=self.alphaBar[0][i]*self.scalefactor[0]
		for t in xrange(self.T-1):
			self.scalefactor[t+1]=0
			for j in xrange(self.N):
				sumalpha=0
				sumAlphaBar=0
				for i in xrange(self.N):
					sumalpha+=self.alpha[t][i]*self.A[i][j]
					sumAlphaBar+=self.alphaHat[t][i]*self.A[i][j]
				self.alpha[t+1][j]=sumalpha*self.B(j,obs[t+1])
				self.alphaBar[t+1][j]=sumAlphaBar*self.B(j,obs[t+1])
				self.scalefactor[t+1]+=self.alphaBar[t+1][j]
			if self.scalefactor[t+1]>0.00000:
				self.scalefactor[t+1]=1.0/self.scalefactor[t+1]
			else:
				self.scalefactor[t+1]=1.0
			for i in xrange(self.N):
				self.alphaHat[t+1][i]=self.alphaBar[t+1][i]*self.scalefactor[t+1]
	def backward(self,obs):
		for i in xrange(self.N):
			self.beta[self.T-1][i]=1
			self.betaBar[self.T-1][i]=1
		for i in xrange(self.N):
			self.betaHat[self.T-1][i]=1*self.scalefactor[self.T-1]
		for t in xrange(self.T-1-1,-1,-1):
			for i in xrange(self.N):
				sumBetaJ=0
				sumBetaBarJ=0
				for j in xrange(self.N):
					sumBetaJ+=self.A[i][j]*self.B(j,obs[t+1])*self.beta[t+1][j]
					sumBetaBarJ+=self.A[i][j]*self.B(j,obs[t+1])*self.betaHat[t+1][j]
				self.beta[t][i]=sumBetaJ
				self.betaHat[t][i]=sumBetaBarJ*self.scalefactor[t]
	def viterbi(self,obs):
		for i in xrange(self.N):
			self.delta[0][i]=self.pi[i]*self.B(i,obs[0])
			self.psi[0][i]=-1
		for t in xrange(1,self.T):
			for j in xrange(self.N):
				maxVal=0
				maxArg=0
				for i in xrange(self.N):
					if self.delta[t-1][i]<0.01:
						self.delta[t-1][i]*=100.0
					tmp=self.delta[t-1][i]*self.A[i][j]
					if tmp>maxVal:
						maxVal=tmp
						maxArg=i
#						print maxVal,maxArg
				self.delta[t][j]=maxVal*self.B(j,obs[t])
				self.psi[t][j]=maxArg
	def initB(self):
		if _1DGAUSS:
			N=self.N
			M=self.M
			self._B=array(N)
			for i in xrange(N):
				mu=i
				sigmaSq=1.0
				self._B[i]=Mixture(mu,sigmaSq)
		elif _KDGAUSS:
			N=self.N
			M=self.M
			self._B=matrix(N,M,1.0/N)
			randomizeMatrix(self._B)
		else:
			N=self.N
			M=self.M
			self._B=matrix(N,M,1.0/N)
			randomizeMatrix(self._B)
	def updateB(self,obs):
		N=self.N
		M=self.M
		T=self.T
		if _1DGAUSS:
			for j in xrange(N):
				for k in xrange(M):
					gammaObsSymbVk=0
					gammaVar=0
					sumGamma=0
					for t in xrange(T):
						sumGamma+=self.gamma[t][j]
						if obs[t]==k:
							gammaObsSymbVk+=self.gamma[t][j]
							gammaVar+=self.gamma[t][j]*(obs[t]-self._B[j].mu)**2
					if PREVENTDIVIDEBYZERO:
						if sumGamma==0:
							sumGamma=1
					self._B[j].mu=gammaObsSymbVk/sumGamma
					self._B[j].sigmaSq=gammaVar/sumGamma
		elif _KDGAUSS:
			self._B[0][0]=0
		else:
			for j in xrange(N):
				for k in xrange(M):
					gammaObsSymbVk=0
					sumGamma=0
					for t in xrange(T):
						sumGamma+=self.gamma[t][j]
						if obs[t]==k:
							gammaObsSymbVk+=self.gamma[t][j]
					if PREVENTDIVIDEBYZERO:
						if sumGamma==0:
							sumGamma=1
					self._B[j][k]=gammaObsSymbVk/sumGamma
	def B(self,a,b):
		if _1DGAUSS:
			return math.exp(-0.5*(b-self._B[a].mu)**2/self._B[a].sigmaSq)/(math.sqrt(2*math.pi*self._B[a].sigmaSq))
		elif _KDGAUSS:
			return self._B[a][b]
		else:
			return self._B[a][b]
	def update(self,obs):
		if NOSCALEFACTOR:
			alpha=self.alpha
			beta=self.beta
		else:
			alpha=self.alphaHat
			beta=self.betaHat
		N=self.N
		M=self.M
		T=self.T
		for t in xrange(T-1):
			tmp=0
			self.pObsGivenModel[t]=0
			for i in xrange(N):
				for j in xrange(N):
					tmp+=self.alpha[t][i]*self.A[i][j]*self.B(j,obs[t+1])*self.beta[t+1][j]
				self.pObsGivenModel[t]+=self.alpha[t][i]*self.beta[t][i]
#			self.pObsGivenModel[t]=tmp
			normalizer=tmp
			#print self.pObsGivenModel[t],tmp
			#assert abs(self.pObsGivenModel[t]-tmp)<0.00001
#			if PREVENTDIVIDEBYZERO:
#				if normalizer==0:
#					normalizer=1
			for i in xrange(N):
				xij=0
				sumXijJ=0
				sumXijHatJ=0
				for j in xrange(N):
					if PREVENTDIVIDEBYZERO:
						if normalizer==0:
							print 'norm 0'
					#		normalizer=1
							xij=self.alpha[t][i]*self.A[i][j]*self.B(j,obs[t+1])*self.beta[t+1][j]
							xijHat=self.alphaHat[t][i]*self.A[i][j]*self.B(j,obs[t+1])*self.betaHat[t+1][j]
							print xij,xijHat
					xij=self.alpha[t][i]*self.A[i][j]*self.B(j,obs[t+1])*self.beta[t+1][j]/normalizer
					xijHat=self.alphaHat[t][i]*self.A[i][j]*self.B(j,obs[t+1])*self.betaHat[t+1][j]
#					print xij,xijHat
					assert abs(xij-xijHat)<0.000001
					self.xi[t][i][j]=xij
					sumXijJ+=xij
					sumXijHatJ+=xijHat
				self.gamma[t][i]=sumXijJ
				assert abs(sumXijJ-sumXijHatJ)<0.000001
		for i in xrange(N):
			self.pi[i]=self.gamma[0][i]
		for i in xrange(N):
			for j in xrange(N):
				sumXi=0
				sumGamma=0
				for t in xrange(T-1):
					sumXi+=self.xi[t][i][j]
					sumGamma+=self.gamma[t][i]
				if PREVENTDIVIDEBYZERO:
					if sumGamma==0:
						sumGamma=1
				self.A[i][j]=sumXi/sumGamma
		self.updateB(obs)
