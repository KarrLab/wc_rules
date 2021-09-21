from pathlib import Path
import sys

def add_models_folder(pathstr):
	path = str(Path(pathstr).resolve())
	sys.path.insert(0,path)
	return

def build_objects(classes,names):
	return [c(n) for c,n in zip(classes,names)]