import random
import sys
import hmm
import myprint
import threading
import tasks
runEvent=threading.Event()
TRIALS=5
STATES=3
SYMBOLS=3
OBSERVATIONS=50
OBSERVATIONS=60
UPDATES=20
TESTOBS=OBSERVATIONS/2
NOISEVAR=0.5
def inputHandler(records):
	while runEvent.is_set():
		inp=raw_input()
		try:
			if inp=='q':
				runEvent.clear()
			elif inp=='info':
				records[-1]['models'].info()
			elif inp=='r':
				runTest()
			else:
				for r in records:
					if inp in r:
						print r[inp]
		except:
			info=sys.exc_info()
			print 'exception:'
			for i in info:
				print i
def runTest(testIter,records):
	for trial in xrange(TRIALS):
		record={}
		records.append(record)
		model=hmm.HMM(STATES,SYMBOLS,OBSERVATIONS)
		model=hmm.GMM(STATES,SYMBOLS,OBSERVATIONS)
		record['models']=model
		task=tasks.JarTask()
		noisyObs=[]
		trueObs=[]
		task.getNoisy(OBSERVATIONS,0,NOISEVAR,trueObs,noisyObs)
		for t in xrange(UPDATES):
			model.train(noisyObs)
		correct=0
		randomCorrect=0
		details=''
		for t in xrange(TESTOBS):
			if not runEvent.is_set():
				return
			details+='test iter:'+str(t)+'\n'
			(prediction,state)=model.predict()
			o=task.draw()
			if o==prediction:
				correct+=1
			if random.randint(0,SYMBOLS)==o:
				randomCorrect+=1
			details+='state:'+str(state)+'\n'
			details+='predicted:'+str(prediction)+'\n'
			details+='drew:'+str(o)+'\n'
			task.getSingleNoisy(0,NOISEVAR,trueObs,noisyObs)
			for t in xrange(UPDATES):
				model.train(noisyObs)
		stats=''
		stats+='correct/testobs=\t%d\t%d\n'%(correct,TESTOBS)
		stats+='random correct/testobs=\t%d\t%d\n'%(randomCorrect,TESTOBS)
		record['stats']=stats
		record['details']=details
	print 'finished test iteration #%d.  type q to exit.'%testIter
	print record.keys()
def main(argv):
	records=[]
	runEvent.set()
	inpHand=threading.Thread(None,inputHandler,'inputHandler',[records])
	inpHand.start()
	i=1
	while runEvent.is_set():
		record={}
		runTest(i,records)
		i+=1
if __name__=='__main__':
	main(sys.argv)
