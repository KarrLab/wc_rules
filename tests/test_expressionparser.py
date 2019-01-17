
from wc_rules.expr2 import parser, get_dependencies
import unittest


list_of_strings = '''
x1 = a.start
x2 = a.end
x3 = b.get_sequence(start=x1,end=x2)
x3 == "ATCG"
c.ph == d.mth
e.ph + f.mth <= 5e-1
{a:a,b:b,c:c,d:d} in p1
count({a:a,b:b} in p2) > 0
pow(a,2) + pow(b,2) - 2*a*b == pow((a-b),2)
any(c.ph,d.mth,{a:a,b:b} in p3)
'''

class TestExpressionParser(unittest.TestCase):
	def test_simpleparse(self):
		tree = parser.parse(list_of_strings)
		deplist = get_dependencies(tree)
