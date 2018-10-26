import random
import myprint
import math
import datatype
MINVAR=0.01
PREVENTDIVIDEBYZERO=True
_1DGAUSS=True
_1DGAUSS=False
_KDGAUSS=True
_KDGAUSS=False
def randomizeMatrix(mat):
	M=len(mat)
	N=len(mat[0])
	for i in xrange(M):
		for j in xrange(N):
			mat[i][j]=random.randint(5,100)/100.0
class CodeTable:
	def __init__(self,M):
		self.tableProb=datatype.array(M,1.0/M)
		for i in xrange(M):
			self.tableProb[i]=random.randint(5,100)/100.0
	def value(self,obs):
		return self.tableProb[int(round(obs))]
	def printParams(self):
		myprint.pprinta(self.tableProb)
	def update(self,i,newVal):
		self.tableProb[i]=newVal
class Gaussian:
	def __init__(self,mu,sigmaSq):
		self.mu=mu
		self.sigmaSq=sigmaSq
	def value(self,obs):
		return math.exp(-0.5*(obs-self.mu)**2/self.sigmaSq)/(math.sqrt(2*math.pi*self.sigmaSq))
	def printParams(self):
		print '%.2e,%.2e'%(self.mu,self.sigmaSq)
class Mixture:
	def __init__(self,mus,sigmaSqs):
		m=len(mus)
		self.M=m
		self.c=datatype.array(m,1.0/m)
		self.gaussians=[]
		for i in xrange(self.M):
			self.gaussians.append(Gaussian(mus[i],sigmaSqs[i]))
	def value(self,obs):
		val=0
		for m in xrange(self.M):
			val+=self.c[m]*self.gaussians[m].value(obs)
		return val
	def printParams(self):
		myprint.pprinta(self.c)
		for g in self.gaussians:
			print '%.2e'%g.mu,
		print
class HMM:
	def __init__(self,STATES,SYMBOLS,OBSERVATIONS):
		self.N=STATES
		self.M=SYMBOLS
		self.T=OBSERVATIONS
		N=self.N
		M=self.M
		T=self.T
		self.A=datatype.matrix(N,N,1.0/STATES)
		self.initB()
		self.pi=datatype.array(N,1.0/STATES)
		self.alpha=datatype.matrix(T,N)
		self.beta=datatype.matrix(T,N)
		self.alphaBar=datatype.matrix(T,N)
		self.betaBar=datatype.matrix(T,N)
		self.alphaHat=datatype.matrix(T,N)
		self.betaHat=datatype.matrix(T,N)
		self.delta=datatype.matrix(T,N)
		self.psi=datatype.matrix(T,N)
		self.xi=datatype.tensor(T,N,N)
		self.gamma=datatype.matrix(T,N)
		self.scalefactor=datatype.array(T,0)
		self.pObsGivenModel=datatype.array(T)
	def train(self,obs):
		self.forward(obs)
		self.backward(obs)
		self.viterbi(obs)
		self.update(obs)
	def getPState(self):
		pState=datatype.array(self.M,0.0)
		eState=self.getExpState()
		for s in xrange(self.N):
			pState[s]=eState[s]/self.T
		return pState
	def getExpState(self):
		expState=datatype.array(self.M,0.0)
		for j in xrange(self.M):
			for t in xrange(self.T):
				expState[j]+=self.gamma[t][j]
		return expState
	def obsProb(self):
		pSymb=datatype.array(self.M,0.0)
		for j in xrange(self.M):
			for i in xrange(self.N):
				pSymb[j]+=self.B(i,j)
		norm=sum(pSymb)
		if PREVENTDIVIDEBYZERO:
			if norm==0:
				norm=1
		for j in xrange(self.M):
			pSymb[j]/=norm
		return pSymb
	def info(self):
		for x in self._B:
			x.printParams()
		print 'pi =',
		myprint.pprinta(self.pi)
		print 'A =',
		myprint.pprint(self.A)
#		print 'alpha =',
#		myprint.pprint(self.alpha)
#		print 'beta =',
#		myprint.pprint(self.beta)
#		print 'delta =',
#		myprint.pprint(self.delta)
#		print 'psi =',
#		myprint.pprint(self.psi)
#		print 'scalefactor =',
#		myprint.pprinta(self.scalefactor)
		eState=self.getExpState()
		print 'eState =',
		myprint.pprinta(eState)
		pState=self.getPState()
		print 'pState =',
		myprint.pprinta(pState)
		pSymb=self.obsProb()
		T=self.T
		tmp=self.delta[T-1][0]
		maxArg=0
		for i in xrange(1,self.N):
			if self.delta[T-1][i]>tmp:
				tmp=self.delta[T-1][i]
				maxArg=i
		t=T-1
		stateTrace=[]
		while t>=0:
#			print maxArg,
			stateTrace.append(maxArg)
			maxArg=self.psi[t][maxArg]
			t-=1
		stateTrace.reverse()
		print 'sta:',
		print stateTrace
		print 'pSymb =',
		myprint.pprinta(pSymb)
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
				for i in xrange(self.N):
					tmp=self.delta[t-1][i]*self.A[i][j]
					if tmp>maxVal:
						maxVal=tmp
						maxArg=i
#						print maxVal,maxArg
				self.delta[t][j]=maxVal*self.B(j,obs[t])
				self.psi[t][j]=maxArg
	def initB(self):
		N=self.N
		M=self.M
		if _1DGAUSS:
			self._B=datatype.array(N)
			for i in xrange(N):
				mu=i+0.1
				sigmaSq=1.0
				self._B[i]=Gaussian(mu,sigmaSq)
		elif _KDGAUSS:
			self._B=datatype.array(N)
			for j in xrange(N):
				mus=[]
				sigmaSqs=[]
				for k in xrange(M):
					mu=k+0.1*j
					sigmaSq=1.0
					mus.append(mu)
					sigmaSqs.append(sigmaSq)
				self._B[j]=Mixture(mus,sigmaSqs)
		else:
			self._B=datatype.array(N)
			for i in xrange(N):
				self._B[i]=CodeTable(M)
	def updateB(self,obs):
		N=self.N
		M=self.M
		T=self.T
		for j in xrange(N):
			if _1DGAUSS:
				for k in xrange(M):
					gammaObsSymbVk2=0
					sumGamma2=0
					gammaVar=0
					for t in xrange(T):
						gammaObsSymbVk2+=self.gamma[t][j]*obs[t]
						sumGamma2+=self.gamma[t][j]
						gammaVar+=self.gamma[t][j]*(obs[t]-self._B[j].mu)**2
#					if PREVENTDIVIDEBYZERO:
#						if sumGamma==0:
#							sumGamma=0.5
#					print self._B[j].mu
					self._B[j].mu=gammaObsSymbVk2/sumGamma2
					self._B[j].sigmaSq=gammaVar/sumGamma2
					if self._B[j].sigmaSq<MINVAR:
						self._B[j].sigmaSq=MINVAR
			elif _KDGAUSS:
				sumGammatjkTK=0
				for k in xrange(M):
					sumGammatjkT=0
					gammatjkdotobs=0
					for t in xrange(T):
						gammatjk=self.gamma[t][j]*self._B[j].c[k]*self._B[j].gaussians[k].value(obs[t])/self._B[j].value(obs[t])
						sumGammatjkT+=gammatjk
						gammatjkdotobs+=gammatjk*obs[t]
					if sumGammatjkT==0:
						sumGammatjkT=1
					self._B[j].c[k]=sumGammatjkT
					self._B[j].gaussians[k].mu=gammatjkdotobs/sumGammatjkT
					sumGammatjkTK+=sumGammatjkT
				for k in xrange(M):
					self._B[j].c[k]/=sumGammatjkTK
			else:
				for k in xrange(M):
					gammaObsSymbVk=0
					sumGamma=0
					for t in xrange(T):
						sumGamma+=self.gamma[t][j]
						if int(round(obs[t]))==k:
							gammaObsSymbVk+=self.gamma[t][j]
					if PREVENTDIVIDEBYZERO:
						if sumGamma==0:
							sumGamma=0.5
#					self._B[j][k]=gammaObsSymbVk/sumGamma
					self._B[j].update(k,gammaObsSymbVk/sumGamma)
	def B(self,state,obs):
		return self._B[state].value(obs)
	def update(self,obs):
		N=self.N
		M=self.M
		T=self.T
		for t in xrange(T-1):
			for i in xrange(N):
				sumXijHatJ=0
				for j in xrange(N):
					xijHat=self.alphaHat[t][i]*self.A[i][j]*self.B(j,obs[t+1])*self.betaHat[t+1][j]
					self.xi[t][i][j]=xijHat
					sumXijHatJ+=xijHat
				self.gamma[t][i]=sumXijHatJ
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
						sumGamma=0.5
				self.A[i][j]=sumXi/sumGamma
		self.updateB(obs)
