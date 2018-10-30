import random
import myprint
import math
import datatype
ONE=1.0
PIWEIGHT=0.1
AWEIGHT=0.1
BWEIGHT=0.1
class CodeTable:
	def __init__(self,M,codewords):
		self.tableProb=datatype.array(M,1.0/M)
		for i in xrange(M):
			self.tableProb[i]=random.randint(0,100)/100.0
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
			print '%.2f'%g.mu,
		print
def randomize(A):
	m=len(A)
	n=len(A[0])
	for i in xrange(m):
		sumRow=0
		for j in xrange(n):
			A[i][j]=random.randint(1,1000)*1.0
			sumRow+=A[i][j]
		for j in xrange(n):
			A[i][j]/=sumRow
class HMM(object):
	def __init__(self,STATES,SYMBOLS,OBSERVATIONS,TRAININGITERS,codewords,MAXSEQ):
		self.observedSeq=0
		self.MAXSEQ=MAXSEQ
		self.name='Code Table Model'
		self.codewords=codewords
		self.trainingIters=TRAININGITERS
		self.N=STATES
		self.M=SYMBOLS
		self.T=OBSERVATIONS
		N=self.N
		M=self.M
		T=self.T
		self.A=datatype.matrix(N,N,1.0/STATES)
		randomize(self.A)
		self.initB(codewords)
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
		self.probObsGivenModel=0
		self.prevProbObsGivenModel=0
		self.scalefactor=datatype.array(T)
		self.tC=datatype.matrix(N,M)
		self.tMu=datatype.matrix(N,M)
		self.tSigmaSq=datatype.matrix(N,M)
		self.xi=datatype.tensor(T,N,N)
		self.gammaInitial=datatype.matrix(MAXSEQ,N)
		self.sumGammaObsT=datatype.matrix(MAXSEQ,N)
		self.sumGammaT=datatype.matrix(MAXSEQ,N)
		self.sumXiT=datatype.tensor(MAXSEQ,N,N)
	def train(self,obs):
		self.observedSeq+=1
		if self.observedSeq>self.MAXSEQ:
			print 'max seq reached'
			return
		for i in xrange(self.trainingIters):
			self.forward(obs)
			if self.probObsGivenModel<self.prevProbObsGivenModel:
				print 'at training iteration %d'%i
				print 'unable to optimize any further'
				assert False
				return
			self.prevProbObsGivenModel=self.probObsGivenModel
			self.backward(obs)
			self.viterbi(obs)
			self.update(obs)
	def getPState(self):
		pState=datatype.array(self.N,0.0)
		eState=self.getExpState()
		for s in xrange(self.N):
			pState[s]=eState[s]/self.T
		return pState
	def getExpState(self):
		expState=datatype.array(self.N,0.0)
		for j in xrange(self.N):
			for t in xrange(self.T):
				expState[j]+=self.gamma[t][j]
		return expState
	def obsProb(self):
		pSymb=datatype.array(self.M,0.0)
		for j in xrange(self.M):
			for i in xrange(self.N):
				pSymb[j]+=self.B(i,j)
		norm=sum(pSymb)
		for j in xrange(self.M):
			pSymb[j]/=norm
		return pSymb
	def info(self):
		print self.name
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
		confidence=tmp
		return self.codewords[maxArg],state,confidence
	def forward(self,obs):
		sumAlphaBar=0
		for i in xrange(self.N):
			self.alpha[0][i]=self.pi[i]*self.B(i,obs[0])
			self.alphaBar[0][i]=self.alpha[0][i]
			sumAlphaBar+=self.alphaBar[0][i]
		if sumAlphaBar>0.00000:
			self.scalefactor[0]=1.0/sumAlphaBar
#			assert self.scalefactor>1
		else:
			self.scalefactor[0]=ONE
		for i in xrange(self.N):
			self.alphaHat[0][i]=self.alphaBar[0][i]*self.scalefactor[0]
		for t in xrange(self.T-1):
			self.scalefactor[t+1]=0
			for j in xrange(self.N):
				sumAlphaHatI=0
				sumAlphaI=0
				for i in xrange(self.N):
					sumAlphaI+=self.alpha[t][i]*self.A[i][j]
					sumAlphaHatI+=self.alphaHat[t][i]*self.A[i][j]
				self.alpha[t+1][j]=sumAlphaI*self.B(j,obs[t+1])
				self.alphaBar[t+1][j]=sumAlphaHatI*self.B(j,obs[t+1])
				self.scalefactor[t+1]+=self.alphaBar[t+1][j]
			if self.scalefactor[t+1]>0.00000:
				self.scalefactor[t+1]=1.0/self.scalefactor[t+1]
#				assert self.scalefactor>1
			else:
				self.scalefactor[t+1]=ONE
			for i in xrange(self.N):
				self.alphaHat[t+1][i]=self.alphaBar[t+1][i]*self.scalefactor[t+1]
		self.probObsGivenModel=0
		for i in xrange(self.N):
			self.probObsGivenModel+=self.alpha[self.T-1][i]
	def backward(self,obs):
		for i in xrange(self.N):
			self.beta[self.T-1][i]=1
			self.betaBar[self.T-1][i]=1
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
				for i in xrange(self.N):
					if self.delta[t-1][i]<0.1 and self.delta[t-1][i]>0:
						for z in xrange(self.N):
							self.delta[t-1][z]*=1000000.0
				randomArg=random.randint(0,self.N-1)
				maxArg=randomArg
				maxVal=self.delta[t-1][maxArg]*self.A[maxArg][j]
				for i in xrange(self.N):
					tmp=self.delta[t-1][i]*self.A[i][j]
					if tmp>maxVal:
						maxVal=tmp
						maxArg=i
#						print maxVal,maxArg
				self.delta[t][j]=maxVal*self.B(j,obs[t])
				self.psi[t][j]=maxArg
	def initB(self,codewords):
		N=self.N
		M=self.M
		self._B=datatype.array(N)
		for i in xrange(N):
			self._B[i]=CodeTable(M,codewords)
	def updateB(self,obs):
		N=self.N
		M=self.M
		T=self.T
		for j in xrange(N):
			sumGamma=0
			for t in xrange(T):
				sumGamma+=self.gamma[t][j]
			if sumGamma!=0:
				for k in xrange(M):
					gammaObsSymbVk=0
					for t in xrange(T):
						#if abs(round(obs[t])-self.codewords[k])<0.0001:
						if round(obs[t])==self.codewords[k]:
							gammaObsSymbVk+=self.gamma[t][j]
					self._B[j].update(k,gammaObsSymbVk/sumGamma)
			else:
				pass
#				print 'gamma zero.  unable to optimize...'
	def B(self,state,obs):
		return self._B[state].value(obs)
	def update(self,obs):
		N=self.N
		M=self.M
		T=self.T
		for t in xrange(T):
			for k in xrange(N):
				self.gamma[t][k]+=self.alphaHat[t][k]*self.betaHat[t][k]/self.scalefactor[t]
		for t in xrange(T-1):
			for i in xrange(N):
				sumXijJ=0
				for j in xrange(N):
					xij=self.alphaHat[t][i]*self.A[i][j]*self.B(j,obs[t+1])*self.betaHat[t+1][j]
					if xij==0 and self.beta[t][i]>0:
						xij=self.gamma[t][i]/self.beta[t][i]*self.A[i][j]*self.B(j,obs[t+1])*self.beta[t+1][j]
					#xij=self.alpha[t][i]*self.A[i][j]*self.B(j,obs[t+1])*self.beta[t+1][j]/self.probObsGivenModel
					self.xi[t][i][j]=xij
					sumXijJ+=xij
				if sumXijJ>0:
					self.gamma[t][i]=sumXijJ
				else:
					for k in xrange(N):
						self.gamma[t][k]+=self.alphaHat[t][k]*self.betaHat[t][k]/self.scalefactor[t]
		for i in xrange(N):
			self.gamma[T-1][i]=self.alphaHat[T-1][i]*self.betaHat[T-1][i]/self.scalefactor[T-1]
		sumPi=0
		for i in xrange(N):
			tmp=0
			for j in xrange(N):
				tmp+=self.pi[j]*self.B(j,obs[0])
			self.gammaInitial[self.observedSeq][i]=self.gamma[0][i]
			if tmp==0:
				self.pi[i]=self.gamma[0][i]
			else:
				#tmp=self.pi[i]*self.B(i,obs[0])/tmp
				tmp=(self.pi[i]*self.B(i,obs[0])+PIWEIGHT)/(tmp+self.N*PIWEIGHT)
				self.pi[i]=tmp
			sumPi+=self.pi[i]
		if sumPi==0:
			for i in xrange(N):
				self.pi[i]=random.randint(1,10)*1.0
			sumPi=0
			for i in xrange(N):
				sumPi+=self.pi[i]
			for i in xrange(N):
				self.pi[i]/=sumPi
		elif sumPi<0.9:
			for i in xrange(N):
				self.pi[i]/=sumPi
		for i in xrange(N):
			sumGammaT=0
			for t in xrange(T-1):
				sumGammaT+=self.gamma[t][i]
			self.sumGammaT[self.observedSeq][i]=sumGammaT
			renormReq=False
			for j in xrange(N):
				sumXiT=0
				for t in xrange(T-1):
					sumXiT+=self.xi[t][i][j]
				self.sumXiT[self.observedSeq][i][j]=sumXiT
				self.A[i][j]=(sumXiT+AWEIGHT)/(sumGamma+self.N*AWEIGHT)
		self.updateB(obs)
class GMM(HMM):
	def __init__(self,*args):
		super(GMM,self).__init__(*args)
		self.name='Gaussian Mixture Model'
	def initB(self,codewords):
		N=self.N
		M=self.M
		self._B=datatype.array(N)
		for j in xrange(N):
			mus=[]
			sigmaSqs=[]
			for k in xrange(M):
				mu=2.0*random.randint(0,500)/1000.0-0.25
				sigmaSq=1.0
				mus.append(mu)
				sigmaSqs.append(sigmaSq)
			self._B[j]=Mixture(mus,sigmaSqs)
	def updateB(self,obs):
		N=self.N
		M=self.M
		T=self.T
		for j in xrange(N):
			for k in xrange(M):
				sumGammatjT=0
				sumGammatjkT=0
				gammatjkdotobs=0
				gammatjkdotsumSqDiff=0
				for t in xrange(T):
					gammatjk=self.gamma[t][j]*self._B[j].c[k]*self._B[j].gaussians[k].value(obs[t])/self._B[j].value(obs[t])
					sumGammatjT+=self.gamma[t][j]
					sumGammatjkT+=gammatjk
					gammatjkdotobs+=gammatjk*obs[t]
					gammatjkdotsumSqDiff+=(obs[t]-self._B[j].gaussians[k].mu)**2
				#self._B[j].c[k]=(sumGammatjkT+BWEIGHT)/(sumGammatjT+self.M*BWEIGHT)
				#self._B[j].gaussians[k].mu=(gammatjkdotobs+BWEIGHT)/(sumGammatjkT+self.M*BWEIGHT)
				#self._B[j].gaussians[k].sigmaSq=(gammatjkdotsumSqDiff+BWEIGHT)/(sumGammatjkT+self.M*BWEIGHT)
				self.tC[j][k]=(sumGammatjkT+BWEIGHT)/(sumGammatjT+self.M*BWEIGHT)
				self.tMu[j][k]=(gammatjkdotobs+BWEIGHT)/(sumGammatjkT+self.M*BWEIGHT)
				self.tSigmaSq[j][k]=(gammatjkdotsumSqDiff+BWEIGHT)/(sumGammatjkT+self.M*BWEIGHT)
		for j in xrange(N):
			for k in xrange(M):
				self._B[j].c[k]=self.tC[j][k]
				self._B[j].gaussians[k].mu=self.tMu[j][k]
				self._B[j].gaussians[k].sigmaSq=self.tSigmaSq[j][k]
