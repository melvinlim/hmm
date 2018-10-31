import sys
import hmm
import myprint
import threading
import tasks
import models
import time
import database
MINCONFIDENCE=0
STOREMODELS=False
class Env:
	def __init__(self,mdl,rating):
		self.model=mdl
		self.rating=rating
		self.confidence=0
runEvent=threading.Event()
STATES=3
SYMBOLS=5
MAXOBS=20
TRAININGITERS=10
TESTOBS=10
NOISEVAR=0.5
POSITIVETASK=False
#POSITIVETASK=True
POPULATION=5
if POSITIVETASK:
	codewords=[0,1,2,3,4]
else:
	codewords=[-2,-1,0,1,2]
def inputHandler(records):
	while runEvent.is_set():
		inp=raw_input()
		try:
			if inp=='q':
				runEvent.clear()
			elif inp=='info':
				if len(records)>=3:
					for i in xrange(3):
						print time.asctime(records[-1-i]['gmtime'])
						print records[-1-i]['stats']
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
def runTest(testIter,records,mList):
#	mList.append(models.UniformRandom(codewords[0],codewords[-1]))
	task=tasks.JarTask(POSITIVETASK)
	noisyObsList=[]
	trueObsList=[]
	task.getNoisyTasks(MAXOBS,TESTOBS,0,NOISEVAR,trueObsList,noisyObsList)
	while len(mList)<POPULATION:
		mList.append(Env(hmm.HMM(STATES,SYMBOLS,MAXOBS,TRAININGITERS,codewords,TESTOBS),0))
	averageRating=0
	for env in mList:
		record={}
		correct=0
		noisyObs=noisyObsList[0]
		startTime=time.clock()
		details=''
		for t in xrange(TESTOBS):
			if not runEvent.is_set():
				return
			details+='test iter:'+str(t)+'\t'
			env.model.train(noisyObs)
			(prediction,state,confidence)=env.model.predict()
			env.confidence+=confidence
			noisyObs=noisyObsList[t]
			trueObs=trueObsList[t]
			o=trueObs[-1]
			if o==prediction:
				correct+=1
			details+='state:'+str(state)+'\t'
			details+='predicted:'+str(prediction)+'\t'
			details+='drew:\t%s,\t%s\n'%(str(o),str(noisyObs[-1]))
		record['models']=env.model
		record['name']=env.model.name
		record['details']=details
		record['correct']=correct
		env.rating=correct
		averageRating+=correct
		stats='[%s]\tcorrect/testobs=\t%d\t%d'%(env.model.name,record['correct'],TESTOBS)
		stats+='\t%f'%(time.clock()-startTime)
		record['stats']=stats
		record['gmtime']=time.gmtime()
		record['time']=time.time()
		records.append(record)
		print details
		print stats
	print 'finished test iteration #%d.  type q to exit.'%testIter
	averageRating/=POPULATION
	print averageRating
	toRemove=[]
	for i in xrange(len(mList)):
#		print mList[i].confidence
		if mList[i].rating<averageRating:
			toRemove.append(mList[i])
		elif mList[i].confidence<=MINCONFIDENCE:
			print 'sumConf<minConf for model id #%d'%i
			toRemove.append(mList[i])
	for x in toRemove:
		print 'removed: %d\n'%x.rating
		mList.remove(x)
	print record.keys()
def main(argv):
	records=[]
	if STOREMODELS:
		db=database.Database('db.sqlite3')
		db.getRecords(records)
	runEvent.set()
	inpHand=threading.Thread(None,inputHandler,'inputHandler',[records])
	inpHand.start()
	i=1
	mList=[]
	for i in xrange(POPULATION):
		mList.append(Env(hmm.HMM(STATES,SYMBOLS,MAXOBS,TRAININGITERS,codewords,TESTOBS),0))
	newRecords=[]
	while runEvent.is_set():
		runTest(i,newRecords,mList)
		i+=1
	if len(newRecords)>=3:
		for i in xrange(3):
			print time.asctime(newRecords[-1-i]['gmtime'])
			print newRecords[-1-i]['stats']
			newRecords[-1-i]['models'].info()
			print
	if STOREMODELS:
		for record in newRecords:
			db.insertRecord(record)
if __name__=='__main__':
	main(sys.argv)
