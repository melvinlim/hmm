import sys
import time
import database
NRECORDS=4
def main(argv):
	records=[]
	db=database.Database('db.sqlite3')
	db.getRecords(records)
	if len(records)>=NRECORDS:
		for i in xrange(NRECORDS):
			print time.asctime(records[-1-i]['gmtime'])
			print records[-1-i]['stats']
			records[-1-i]['models'].info()
			print
	db.deleteWhere('name','Uniform Random Model')
if __name__=='__main__':
	main(sys.argv)
