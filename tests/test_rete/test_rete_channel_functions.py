from wc_rules.matcher.functionalize2 import *
from wc_rules.matcher.core import *
from wc_rules.schema.base import BaseClass
from wc_rules.graph.examples import *
from wc_rules.graph.canonical_labeling import canonical_label
import unittest

class X(BaseClass):
	pass
class Y(X):
	pass

def make_token(entry={},action=''):
	return {'entry':entry,'action':action}

class TestReteChannelFunctions(unittest.TestCase): 

	def test_pass_channel(self):
		pass
