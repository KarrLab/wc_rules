
from wc_rules.expr2 import parser, get_dependencies, BuiltinHook
import math
import unittest


list_of_strings = '''
x1 = a.start
x2 = a.end
x3 = b.get_sequence(start=x1,end=x2)
x3 == "ATCG"
c.ph == d.mth
e.ph + f.mth <= 5e-1
exists({a:a,b:b,c:c,d:d} in p1)
count({a:a,b:b} in p2) > 0
pow(a,2) + pow(b,2) - 2*a*b == pow((a-b),2)
any(c.ph,d.mth,exists({a:a,b:b} in p3))
'''

class TestExpressionParser(unittest.TestCase):
	def test_simpleparse(self):
		tree = parser.parse(list_of_strings)
		deplist = get_dependencies(tree)

	def test_builtinhook(self):
		h = BuiltinHook()

		tuplist = [
			(h.abs(-1),1),
			(h.ceil(0.1),1),
			(h.factorial(4),24),
			(h.floor(2.1),2),
			(h.sum(.1,.1,.1,.1),.4),
			(h.exp(1),math.e),
			(h.expm1(1),math.e-1),
			(h.log(math.e),1),
			(h.log(100,10),2),
			(h.log1p(math.e-1),1),
			(h.log2(4),2),
			(h.log10(100),2),
			(h.pow(2,3),8),
			(h.sqrt(9),3),
			(h.acos(0),h.pi/2),
			(h.asin(1),h.pi/2),
			(h.atan(1),h.pi/4),
			(h.atan2(1,1),h.pi/4),
			(h.cos(0),1),
			(h.sin(h.pi/2),1),
			(h.tan(0),0),
			(h.degrees(h.pi/2),90),
			(h.radians(90),h.pi/2),
			(h.tau,h.pi*2),
			(h.hypot(1,1),h.sqrt(2)),
			(h.max(1,2,3),3),
			(h.min(-1,-2,-3),-3),

			(h.sum(1,2,3),6),
			(h.any(True,False,False),True),
			(h.all(True,False,False),False),
			(h.any(False,False,False),False),
			(h.all(True,True,True),True),
			(h.notf(True),False),
			(h.notf(False),True),
		]

		for x,y in tuplist:
			self.assertEqual(x,y)

		