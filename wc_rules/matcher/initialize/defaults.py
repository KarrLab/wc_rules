from .schema import *

default_initialization_methods = [method for name,method in globals().items() if name.startswith('initialize_')]