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
				if len(records)>=3:
					for i in xrange(3):
						records[-1-i]['models'].info()
						print
				else:
					print 'records not yet available'
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
		noisyObsList=[]
		trueObsList=[]
		task.getNoisyTasks(MAXOBS,TESTOBS,0,NOISEVAR,trueObsList,noisyObsList)
		noisyObs=noisyObsList[0]
		for t in xrange(UPDATES):
			for model in mList:
				model.train(noisyObs)
		noisyObsList.pop(0)
		trueObsList.pop(0)
		for model in mList:
			for t in xrange(TESTOBS):
				if not runEvent.is_set():
					return
				correct=0
				details='test iter:'+str(t)+'\t'
				(prediction,state)=model.predict()
				noisyObs=noisyObsList[t]
				trueObs=trueObsList[t]
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
			stats='[%s] correct/testobs=\t%d\t%d'%(model.name,trialRecords[model]['correct'],TESTOBS)
			trialRecords[model]['stats']=stats
			records.append(trialRecords[model])
			print stats
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
