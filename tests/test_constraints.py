from wc_rules.attributes import *
from wc_rules.entity import Entity
from wc_rules.pattern2 import Scaffold, Pattern
import math
import unittest

class X(Entity):
	i = IntegerAttribute()
	j = IntegerAttribute()

	@localfn
	def total(i,j,k=0):
		return i+j
	
	
class Y(Entity):
	a = BooleanAttribute()
	b = BooleanAttribute()

	x = ManyToOneAttribute(X,related_name='y')

	@localfn
	def a_and_b(a,b,c=True):
		return a and b and c

x = X('x')
y1 = Y('y1',x=x)
y2 = Y('y2',x=x)
sc = Scaffold(x)


px = Pattern(Scaffold(X('x'))).add_constraints('''x.total(k=5) <= 10''')
py = Pattern(Scaffold(Y('y'))).add_constraints('''y.a_and_b() == True''')
p = Pattern(sc).add_helpers(dict(px=px,py=py)).add_constraints('''
		px.contains(x=x) == True
		py.contains(y=y1) == True
		py.contains(y=y2) == True
		v = x.i*x.j
		w = pow(x.i,x.j)
	''')

p1 = Pattern(sc).add_constraints('''
	any(y1.a,y1.b,y2.a,y2.b) == True
	all(y1.a,y1.b,y2.a,y2.b) == True
	inv(all(y1.a,y1.b)) == True
	inv(all(y2.a,y2.b)) == True
	''')

class Z(Entity):
	alpha = FloatAttribute()
	
zsc = Scaffold(Z('z'))
z1 = Pattern(zsc).add_constraints('''
	sin_alpha = sin(radians(z.alpha))
	cos_alpha = cos(radians(z.alpha))
	tan_alpha = tan(radians(z.alpha))

	''')




class TestPattern(unittest.TestCase):

    def test_scaffold(self):
    	labels = sorted([y.id for y in [y1,y2]])
    	self.assertEqual(labels,['y1','y2'])
    	self.assertEqual(len(sc),3)
    	namespace = sc.get_namespace()
    	self.assertTrue(isinstance(namespace,dict))
    	labels = sorted([x.id for x in sc])
    	self.assertEqual(sorted(namespace.keys()),labels)

    def test_constraints(self):
    	self.assertTrue(len(px.constraints)==len(py.constraints)==1)
    	
    	c = px.constraints[0]
    	match = dict(x=X(i=1,j=2))
    	self.assertEqual(c.process(match)[0],True)
    	match = dict(x=X(i=6,j=7))
    	self.assertEqual(c.process(match)[0],False)
    	
    	c = py.constraints[0]
    	match = dict(y=Y(a=True,b=True))
    	self.assertEqual(c.process(match)[0],True)
    	match = dict(y=Y(a=True,b=False))
    	self.assertEqual(c.process(match)[0],False)

    	match = dict(x=X(i=2,j=3))
    	c1 = p.constraints[3]
    	outbool,match = c1.process(match)
    	self.assertEqual(outbool,True)
    	self.assertTrue('v' in match)
    	self.assertEqual(match['v'],6)
    	c2 = p.constraints[4]
    	outbool,match = c2.process(match)
    	self.assertEqual(outbool,True)
    	self.assertTrue('w' in match)
    	self.assertEqual(match['w'],8)

    def test_boolfns(self):
    	match= dict(x=X(),y1=Y(a=True,b=True),y2=Y(a=False,b=True))
    	[c1,c2,c3,c4] = p1.constraints
    	outbool,match =c1.process(match)
    	self.assertEqual(outbool,True)
    	outbool,match =c2.process(match)
    	self.assertEqual(outbool,False)
    	outbool,match =c3.process(match)
    	self.assertEqual(outbool,False)
    	outbool,match =c4.process(match)
    	self.assertEqual(outbool,True)

    def test_trigfns(self):
    	match = dict(z = Z(alpha=30))
    	for c in z1.constraints:
    		outbool,match = c.process(match)
    	assignedvars = ['sin_alpha','cos_alpha','tan_alpha']
    	self.assertEqual([round(match[x],3) for x in assignedvars],
    		[round(x,3) for x in [0.5, math.sqrt(3)/2,math.sqrt(3)/3]])


    def test_pattern(self):
    	with self.assertRaises(AssertionError):
    		Pattern(scaffold=X())
    	self.assertEqual(p.helpers,{'px':px,'py':py})
