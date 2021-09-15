from pathlib import Path
import sys

def add_models_folder(pathstr):
	path = str(Path(pathstr).resolve())
	sys.path.insert(0,path)
	return