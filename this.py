import chromosome as Chr
import sys
import pandas as pd
if __name__ == '__main__':
	file = sys.argv[1]
	reload(Chr)
	a = Chr.Chromosome.loadFasta(file,circular=True)
	print a.__repr__()
	