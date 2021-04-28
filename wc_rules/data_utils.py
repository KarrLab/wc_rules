from copy import deepcopy
import json, importlib.util
import yaml

def write_yaml(_dict,filename=None):
    s = yaml.dump(deepcopy(_dict))
    if filename is not None:
        with open(filename,'w') as file:
            file.write(s)
    return s

def read_yaml(filename):
    with open(filename,'r') as file:
        doc = yaml.load(file)
    return doc

def write_json(_dict,filename):
    with open(filename,'w') as file:
        json.dump(deepcopy(_dict),file,indent=4)
    return