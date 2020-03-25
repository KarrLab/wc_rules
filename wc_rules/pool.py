
from .utils import print_as_tuple, generate_id
class Pool:
	def __init__(self,iterable=[]):
		self._dict = {}
		self.insert(iterable)

	def insert_item(self,item):
		assert item.get_id() not in self._dict
		self._dict[item.get_id()] = item
		return self

	def remove_item(self,item):
		self._dict.pop(item.get_id())
		return self

	def insert(self,items):
		for item in items:
			self.insert_item(item)
		return self

	def remove(self,items):
		for item in items:
			self.remove_item(item)
		return self

	def get(self,idx):
		if idx not in self._dict:
			return None
		return self._dict[idx]

	def fetch(self,idx,_cls=None):
		assert idx in self._dict, "Item doesn't exist in the pool."
		if _cls is not None:
			assert isinstance(self._dict[idx],_cls), "Item doesn't exist in the pool."
		return self._dict[idx]

	def contains(self,_cls=None,idx=None):
		# special method for dealing with node tokens
		if _cls is None:
			return idx in self._dict
		return idx in self._dict and self._dict[idx].__class__ == _cls

	def __len__(self):
		return len(self._dict)

	def __str__(self):
		final_strs = []
		for x in self._dict:
			item = self.get(x)
			idx = x
			_cls = item.__class__.__name__
			literal_attrs = item.get_nonempty_scalar_attributes()
			literal_strs = [print_as_tuple((attr,getattr(item,attr))) for attr in literal_attrs]
			related_attrs = item.get_nonempty_related_attributes()
			related_strs = []
			for attr in related_attrs:
				x = getattr(item,attr)
				if isinstance(x,list):
					tup = (attr,print_as_tuple([y.id for y in x]))
				else:
					tup = (attr,x.id)
				related_strs.append(print_as_tuple(tup))
			strs = literal_strs + related_strs
			state_str = ''
			if len(strs) > 0:
				state_str = ','.join(strs)
			final_strs.append(print_as_tuple((item.__class__.__name__,idx,state_str)))
		return '\n'.join(['[']+final_strs + [']'])

	def idgen(n=1):
		vec = [None]*n
		for i in range(n):
			while vec[i] is None:
				idx = generate_id()
				if idx not in self:
					vec[i] = idx
		return vec


