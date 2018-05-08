


from wc_rules import bioseq,utils

inputstr = 'ATCGAT'
X = bioseq.DNA(ambiguous=False).set_sequence(inputstr)
f = bioseq.PolynucleotideFeature().set_molecule(X)

f.set_location(0,1)
print(X.get_sequence(**f.get_location()))
