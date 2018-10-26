def array(n,xi=0.0):
	return [xi for _ in xrange(n)]
def matrix(m,n,xi=0.0):
	return [[xi for _ in xrange(n)] for _ in xrange(m)]
def tensor(i,j,k,xi=0.0):
	return [[[xi for _ in xrange(k)] for _ in xrange(j)] for _ in xrange(i)]
