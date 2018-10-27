import sqlite3
try:
	import cPickle as pickle
except:
	import pickle
class Database(object):
	def __init__(self,filename):
		self.db=sqlite3.connect(filename)
		self.cursor=self.db.cursor()
		self.createTable('records')
	def printAll(self):
		query='SELECT * FROM records'
		lines=self.cursor.execute(query)
		data=self.cursor.fetchall()
		for i in data:
			print i
	def createTable(self,tableName):
		query='CREATE TABLE IF NOT EXISTS %s (\n'%tableName
		query+='time REAL PRIMARY KEY,\n'
		query+='record BLOB UNIQUE NOT NULL\n'
		query+=');'
		lines=self.cursor.execute(query)
		self.db.commit()
	def insertPyObj(self,obj,tableName):
		pass
	def insertRecord(self,record,tableName='records'):
		pickledData=pickle.dumps(record,-1)
		query='INSERT INTO %s\n'%tableName
		query+='(time, record)\n'
		query+='VALUES\n'
		query+='(?,?);\n'
		lines=self.cursor.execute(query,[float(record['time']),sqlite3.Binary(pickledData)])
		self.db.commit()
	def getRecords(self,records):
		self.cursor.execute('select record from records order by time asc')
		for row in self.cursor:
			record=pickle.loads(str(row[0]))
			records.append(record)
