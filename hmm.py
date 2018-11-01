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
			A[i][j]=random.randint(1,10000)*1.0
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
		#self.gammaInitial=datatype.matrix(MAXSEQ,N)
		#self.sumGammaObsT=datatype.matrix(MAXSEQ,N)
		#self.sumGammaTm1=datatype.matrix(MAXSEQ,N)
		#self.sumGammaT=datatype.matrix(MAXSEQ,N)
		#self.sumXiT=datatype.tensor(MAXSEQ,N,N)
		self.gammaInitial=datatype.array(N)
		self.sumGammaObsT=datatype.matrix(N,M)
		self.sumGammaTm1=datatype.array(N)
		self.sumGammaT=datatype.array(N)
		self.sumXiT=datatype.matrix(N,N)
	def train(self,obs):
		#if self.observedSeq>self.MAXSEQ:
		#	print 'max seq reached'
		#	return
		i=0
		self.obs=obs
		self.prevProbObsGivenModel=0
		self.probObsGivenModel=0
		while i<self.trainingIters and (self.probObsGivenModel>=self.prevProbObsGivenModel):
			self.observedSeq+=1
#			print i,self.probObsGivenModel,self.prevProbObsGivenModel
			self.prevProbObsGivenModel=self.probObsGivenModel
#			self.preventMatchingRows()
			self.forward(obs)
			self.backward(obs)
			self.update(obs)
#			if self.probObsGivenModel<self.prevProbObsGivenModel:
			if self.probObsGivenModel==0:
				print 'at training iteration %d'%i
				print 'pogm==0'
#				print 'unable to optimize any further'
#				assert False
				return
			i+=1
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
			expState[j]/=self.observedSeq
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
		self.viterbi(self.obs)
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
		confidence=self.probObsGivenModel
		return self.codewords[maxArg],state,confidence
	def preventMatchingRows(self):
		N=self.N
		M=self.M
		toRandomize=[]
		for j in xrange(1,N):
			rowSum=0
			for k in xrange(M):
				rowSum+=abs(self._B[j].value(k)-self._B[j-1].value(k))
			if rowSum<0.1:
				toRandomize.append(j)
		for x in toRandomize:
			sumRow=0
			for k in xrange(M):
				self._B[x].update(k,random.randint(0,100)/100.0)
				sumRow+=self._B[x].value(k)
			for k in xrange(M):
				self._B[x].update(k,self._B[x].value(k)/sumRow)
			print 'randomized row %d',x
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
			sumGammaT=0
			for t in xrange(T):
				sumGammaT+=self.gamma[t][j]
			self.sumGammaT[j]+=sumGammaT
			if sumGammaT!=0:
				for k in xrange(M):
					gammaObsSymbVk=0
					for t in xrange(T):
						if abs(round(obs[t])-self.codewords[k])<0.0001:
						#if round(obs[t])==self.codewords[k]:
							gammaObsSymbVk+=self.gamma[t][j]
					self.sumGammaObsT[j][k]+=gammaObsSymbVk
					self._B[j].update(k,self.sumGammaObsT[j][k]/self.sumGammaT[j])
					#self._B[j].update(k,gammaObsSymbVk/sumGammaT)
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
				self.gamma[t][k]=self.alphaHat[t][k]*self.betaHat[t][k]/self.scalefactor[t]
		for t in xrange(T-1):
			for i in xrange(N):
				sumXijJ=0
				for j in xrange(N):
					xij=self.alphaHat[t][i]*self.A[i][j]*self.B(j,obs[t+1])*self.betaHat[t+1][j]
					if xij==0 and self.beta[t][i]>0:
						xij=self.gamma[t][i]/self.beta[t][i]*self.A[i][j]*self.B(j,obs[t+1])*self.beta[t+1][j]
					self.xi[t][i][j]=xij
					sumXijJ+=xij
		sumPi=0
		for i in xrange(N):
			#self.gammaInitial[self.observedSeq][i]=self.gamma[0][i]
			#tmpSum=0
			#for k xrange(self.observedSeq+1):
			#	tmpSum+=self.gammaInitial[k][[i]
			self.gammaInitial[i]+=self.gamma[0][i]
			self.pi[i]=self.gammaInitial[i]*1.0/self.observedSeq
			#self.pi[i]=self.gamma[0][i]
			sumPi+=self.pi[i]
		for i in xrange(N):
			self.pi[i]/=sumPi
		if abs(1.0-sumPi)>0.1:
			for i in xrange(N):
				denom=0
				for k in xrange(self.N):
					denom+=self.pi[k]*self.B(k,obs[0])
				self.pi[i]=(BWEIGHT+self.pi[i]*self.B(i,obs[0]))/(self.N*BWEIGHT+denom)
		for i in xrange(N):
			sumGammaTm1=0
			for t in xrange(T-1):
				sumGammaTm1+=self.gamma[t][i]
			#self.sumGammaTm1[self.observedSeq][i]=sumGammaTm1
			self.sumGammaTm1[i]+=sumGammaTm1
			sumAJ=0
			for j in xrange(N):
				sumXiT=0
				for t in xrange(T-1):
					sumXiT+=self.xi[t][i][j]
				#self.sumXiT[self.observedSeq][i][j]=sumXiT
				self.sumXiT[i][j]+=sumXiT
				self.A[i][j]=(self.sumXiT[i][j]+AWEIGHT)/(self.sumGammaTm1[i]+self.N*AWEIGHT)
				sumAJ+=self.A[i][j]
			for j in xrange(N):
				self.A[i][j]/=sumAJ
				#self.A[i][j]=(sumXiT+AWEIGHT)/(sumGammaTm1+self.N*AWEIGHT)
		self.updateB(obs)
class HMMU(HMM):	#unscaled version of HMM.
	def __init__(self,*args):
		super(HMMU,self).__init__(*args)
		self.name='Unscaled Code Table Model'
	def forward(self,obs):
		for i in xrange(self.N):
			self.alpha[0][i]=self.pi[i]*self.B(i,obs[0])
		for t in xrange(self.T-1):
			for j in xrange(self.N):
				sumAlphaI=0
				for i in xrange(self.N):
					sumAlphaI+=self.alpha[t][i]*self.A[i][j]
				self.alpha[t+1][j]=sumAlphaI*self.B(j,obs[t+1])
		self.probObsGivenModel=0
		for i in xrange(self.N):
			self.probObsGivenModel+=self.alpha[self.T-1][i]
	def backward(self,obs):
		for i in xrange(self.N):
			self.beta[self.T-1][i]=1
		for t in xrange(self.T-1-1,-1,-1):
			for i in xrange(self.N):
				sumBetaJ=0
				for j in xrange(self.N):
					sumBetaJ+=self.A[i][j]*self.B(j,obs[t+1])*self.beta[t+1][j]
				self.beta[t][i]=sumBetaJ
		if self.probObsGivenModel==0:
			for i in xrange(self.N):
				self.probObsGivenModel+=self.beta[0][i]*self.pi[i]*self.B(i,obs[0])
	def update(self,obs):
		N=self.N
		M=self.M
		T=self.T
		#note: probObsGivenModel is the same for every value of t.  therefore, if it is not calculable at a certain value of t, try other values.
		t=0
		while self.probObsGivenModel==0 and t<T:
			for i in xrange(N):
				self.probObsGivenModel+=self.alpha[t][i]*self.beta[t][i]
			t+=1
		if self.probObsGivenModel==0:
			return
		for t in xrange(T):
			for k in xrange(N):
				self.gamma[t][k]=self.alpha[t][k]*self.beta[t][k]/self.probObsGivenModel
		for t in xrange(T-1):
			for i in xrange(N):
				sumXijJ=0
				for j in xrange(N):
					xij=self.alpha[t][i]*self.A[i][j]*self.B(j,obs[t+1])*self.beta[t+1][j]/self.probObsGivenModel
					if xij==0 and self.beta[t][i]>0:
						xij=self.gamma[t][i]/self.beta[t][i]*self.A[i][j]*self.B(j,obs[t+1])*self.beta[t+1][j]
					self.xi[t][i][j]=xij
					sumXijJ+=xij
		sumPi=0
		for i in xrange(N):
			self.gammaInitial[i]+=self.gamma[0][i]
			self.pi[i]=self.gammaInitial[i]*1.0/self.observedSeq
			sumPi+=self.pi[i]
		for i in xrange(N):
			self.pi[i]/=sumPi
		if sumPi==0:
			print 'sumPi was 0'
			assert False
		for i in xrange(N):
			sumGammaTm1=0
			for t in xrange(T-1):
				sumGammaTm1+=self.gamma[t][i]
			self.sumGammaTm1[i]+=sumGammaTm1
			sumAJ=0
			for j in xrange(N):
				sumXiT=0
				for t in xrange(T-1):
					sumXiT+=self.xi[t][i][j]
				self.sumXiT[i][j]+=sumXiT
				self.A[i][j]=(self.sumXiT[i][j]+AWEIGHT)/(self.sumGammaTm1[i]+self.N*AWEIGHT)
				sumAJ+=self.A[i][j]
			for j in xrange(N):
				self.A[i][j]/=sumAJ
		self.updateB(obs)
class GMM(HMM):
	def __init__(self,*args):
		super(GMM,self).__init__(*args)
		self.name='Gaussian Mixture Model'
		N=self.N
		M=self.M
		self.sumGamma2ObsT=datatype.matrix(N,M)
		self.sumGamma2T=datatype.array(N)
	def initB(self,codewords):
		N=self.N
		M=self.M
		self._B=datatype.array(N)
		for j in xrange(N):
			mus=[]
			sigmaSqs=[]
			for k in xrange(M):
				mu=codewords[k]+random.randint(0,500)/1000.0-0.25
				sigmaSq=1.0
				mus.append(mu)
				sigmaSqs.append(sigmaSq)
			self._B[j]=Mixture(mus,sigmaSqs)
	def updateB(self,obs):
		N=self.N
		M=self.M
		T=self.T
		for j in xrange(N):
			sumTCK=0
			for k in xrange(M):
				sumGammatjT=0
				sumGammatjkT=0
				gammatjkdotobs=0
				gammatjkdotsumSqDiff=0
				for t in xrange(T):
					gammatjk=self.gamma[t][j]*self._B[j].c[k]*self._B[j].gaussians[k].value(obs[t])/self._B[j].value(obs[t])
					sumGammatjkT+=gammatjk
					gammatjkdotobs+=gammatjk*obs[t]
					gammatjkdotsumSqDiff+=(obs[t]-self._B[j].gaussians[k].mu)**2
					sumGammatjT+=self.gamma[t][j]
				self.sumGamma2ObsT[j][k]+=gammatjkdotobs
				self.sumGamma2T[j]+=sumGammatjkT
				#self._B[j].c[k]=(sumGammatjkT+BWEIGHT)/(sumGammatjT+self.M*BWEIGHT)
				#self._B[j].gaussians[k].mu=(gammatjkdotobs+BWEIGHT)/(sumGammatjkT+self.M*BWEIGHT)
				#self._B[j].gaussians[k].sigmaSq=(gammatjkdotsumSqDiff+BWEIGHT)/(sumGammatjkT+self.M*BWEIGHT)
#				self.tC[j][k]=(sumGammatjkT+BWEIGHT)/(sumGammatjT+self.M*BWEIGHT)
#				self.tMu[j][k]=(gammatjkdotobs+BWEIGHT)/(sumGammatjkT+self.M*BWEIGHT)
				self.tC[j][k]=(self.sumGamma2T[j]+BWEIGHT)/(self.sumGammaT[j]+self.M*BWEIGHT)
				self.tMu[j][k]=(self.sumGamma2ObsT[j][k]+BWEIGHT)/(self.sumGamma2T[j]+self.M*BWEIGHT)
				sumTCK+=self.tC[j][k]
			for k in xrange(M):
				self.tC[j][k]/=sumTCK
				#self.tSigmaSq[j][k]=(gammatjkdotsumSqDiff+BWEIGHT)/(sumGammatjkT+self.M*BWEIGHT)
		for j in xrange(N):
			for k in xrange(M):
				self._B[j].c[k]=self.tC[j][k]
				self._B[j].gaussians[k].mu=self.tMu[j][k]
				#self._B[j].gaussians[k].sigmaSq=self.tSigmaSq[j][k]
class GMM1D(HMM):
	def __init__(self,*args):
		super(GMM1D,self).__init__(*args)
		self.name='1D Gaussian Mixture Model'
	def initB(self,codewords):
		N=self.N
		M=self.M
		self._B=datatype.array(N)
		for i in xrange(N):
			#mu=codewords[i]+random.randint(0,500)/1000.0-0.25
			mu=codewords[i]+0.1
			sigmaSq=1.0
			self._B[i]=Gaussian(mu,sigmaSq)
	def updateB(self,obs):
		MINVAR=0.5
		N=self.N
		M=self.M
		T=self.T
		for j in xrange(N):
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
	def update(self,obs):
		N=self.N
		M=self.M
		T=self.T
		for t in xrange(T-1):
			for k in xrange(N):
				self.gamma[T-1][k]=self.alphaHat[T-1][k]*self.betaHat[T-1][k]/self.scalefactor[T-1]
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
				#if PREVENTDIVIDEBYZERO:
				if True:
					if sumGamma==0:
						sumGamma=0.5
				self.A[i][j]=sumXi/sumGamma
		self.updateB(obs)
