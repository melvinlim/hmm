import random
import sys
import hmm
import myprint
import threading
import tasks
import models
runEvent=threading.Event()
TRIALS=5
STATES=3
SYMBOLS=3
MAXOBS=60
UPDATES=20
TESTOBS=MAXOBS/2
NOISEVAR=0.5
def inputHandler(records):
	while runEvent.is_set():
		inp=raw_input()
		try:
			if inp=='q':
				runEvent.clear()
			elif inp=='info':
				for i in xrange(3):
					records[-1-i]['models'].info()
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
		trialRecords={}
		mList=[]
		mList.append(hmm.HMM(STATES,SYMBOLS,MAXOBS))
		mList.append(hmm.GMM(STATES,SYMBOLS,MAXOBS))
		mList.append(models.UniformRandom(0,SYMBOLS-1))
		for model in mList:
			record={}
			record['models']=model
			record['details']=''
			record['correct']=0
			trialRecords[model]=record
		task=tasks.JarTask()
		noisyObs=[]
		trueObs=[]
		task.getNoisy(MAXOBS,0,NOISEVAR,trueObs,noisyObs)
		for t in xrange(UPDATES):
			for model in mList:
				model.train(noisyObs)
		correct=0
		randomCorrect=0
		for t in xrange(TESTOBS):
			if not runEvent.is_set():
				return
			for model in mList:
				correct=0
				details='test iter:'+str(t)+'\t'
				(prediction,state)=model.predict()
				task.getSingleNoisy(0,NOISEVAR,trueObs,noisyObs)
				o=trueObs[-1]
				if o==prediction:
					correct+=1
				details+='state:'+str(state)+'\t'
				details+='predicted:'+str(prediction)+'\t'
				details+='drew:'+str(o)+'\n'
				for t in xrange(UPDATES):
					model.train(noisyObs)
				trialRecords[model]['details']+=details
				trialRecords[model]['correct']+=correct
		for model in mList:
			stats='correct/testobs=\t%d\t%d\n'%(trialRecords[model]['correct'],TESTOBS)
			trialRecords[model]['stats']=stats
			records.append(trialRecords[model])
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
