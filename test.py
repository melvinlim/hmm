import random
import sys
import hmm
import myprint
import threading
import tasks
runEvent=threading.Event()
infoEvent=threading.Event()
statEvent=threading.Event()
TRIALS=5
STATES=3
SYMBOLS=3
OBSERVATIONS=50
OBSERVATIONS=60
UPDATES=20
TESTOBS=OBSERVATIONS/2
NOISEVAR=0.5
def inputHandler():
	while runEvent.is_set():
		inp=raw_input()
		try:
			if inp=='q':
				runEvent.clear()
			elif inp=='info':
				infoEvent.set()
			elif inp=='stat':
				statEvent.set()
			elif inp=='r':
				runTest()
		except:
			info=sys.exc_info()
			print 'exception:'
			for i in info:
				print i
def runTest(testIter):
	predictions=[]
	probabilities=[]
	for trial in xrange(TRIALS):
		model=hmm.HMM(STATES,SYMBOLS,OBSERVATIONS)
		task=tasks.JarTask()
		noisyObs=[]
		trueObs=[]
		task.getNoisy(OBSERVATIONS,0,NOISEVAR,trueObs,noisyObs)
		for t in xrange(UPDATES):
			model.train(noisyObs)
		correct=0
		randomCorrect=0
		stats=''
		for t in xrange(TESTOBS):
			if not runEvent.is_set():
				return
			elif statEvent.is_set():
				statEvent.clear()
				print stats
			elif infoEvent.is_set():
				infoEvent.clear()
				model.info()
			stats+='test iter:'+str(t)+'\n'
			(prediction,state)=model.predict()
			o=task.draw()
			if o==prediction:
				correct+=1
			if random.randint(0,SYMBOLS)==o:
				randomCorrect+=1
			stats+='state:'+str(state)+'\n'
			stats+='predicted:'+str(prediction)+'\n'
			stats+='drew:'+str(o)+'\n'
			task.getSingleNoisy(0,NOISEVAR,trueObs,noisyObs)
			for t in xrange(UPDATES):
				model.train(noisyObs)
		print 'correct/testobs=',correct,TESTOBS
		print 'random correct/testobs=',randomCorrect,TESTOBS
		predicted=model.info()
		predictions.append(predicted)
		pSymb=[]
		for i in xrange(SYMBOLS):
			pSymb.append(0.0)
		total=0
		for o in trueObs:
			pSymb[o]+=1.0
			total+=1.0
		for t in xrange(SYMBOLS):
			pSymb[t]/=total
		print 'actual pSymb',
		myprint.pprinta(pSymb)
		probabilities.append(pSymb)
		print 'obs:',
		myprint.pprinta(noisyObs)
#	print 'pred:',
#	myprint.pprint(predictions)
#	print 'prob:',
#	myprint.pprint(probabilities)
	absError=0
	for t in xrange(TRIALS):
		for s in xrange(SYMBOLS):
			absError+=abs(predictions[t][s]-probabilities[t][s])
	print 'absError:',absError*1.0/TRIALS
	print 'finished test iteration #%d.  type q to exit.'%testIter
def main(argv):
	runEvent.set()
	inpHand=threading.Thread(None,inputHandler,'inputHandler')
	inpHand.start()
	i=1
	while runEvent.is_set():
		runTest(i)
		i+=1
if __name__=='__main__':
	main(sys.argv)
