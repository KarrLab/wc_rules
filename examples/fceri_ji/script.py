from model import model

from pprint import pformat
from wc_rules.data_utils import write_yaml, write_json, read_yaml


p = model.collect_parameters()
q = write_yaml(p,'data_fceri_ji.yaml')
r = read_yaml('data_fceri_ji.yaml')
write_json(p,'data_fceri_ji.json')
model.verify(r)
