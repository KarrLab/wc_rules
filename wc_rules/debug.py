import bio
import seq


inputstr = 'TGTCAGGACGTCCTAGATGCTCGATTTGCTGACGCTCAGCTATATCACTTATCCTCGCGGGATCTCGTGCCGAGCTGTAGAGATGTGTGCAGGCCTAACA'
A = bio.DNASequenceMolecule().init_sequence(inputstr,ambiguous=False)
print(A.sequence)
print(A.sequence_length())
x = seq.SimpleSequenceFeature().set_molecule(A)
#A.add_feature(x)
print(A.features)
print(x.molecule)
print(x.position,x.length)
print(x.get_sequence())

#x1 = seq.SimpleSequenceFeature(position=0,length=10).set_molecule(A)
x2 = seq.SimpleSequenceFeature(position=-10,length=10).set_molecule(A)
#print(x1.get_sequence())
f = x2._get_feature_location_object()
print(f.start,f.end)
print(f.extract(A.sequence))
#print(x2.get_sequence())
#xcomp = seq.CompositeSequenceFeature().set_molecule(A).add_feature(x1,x2)
#print(xcomp.get_sequence())
print(A.sequence[:10])
