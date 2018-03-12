"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-12-13
:Copyright: 2017, Karr Lab
:License: MIT
"""

import pkg_resources

with open(pkg_resources.resource_filename('wc_rules', 'VERSION'), 'r') as file:
    __version__ = file.read().strip()
# :obj:`str`: version

# API
from . import base
from . import bio
from . import chem
from . import entity
from . import filter
from . import graph_utils
from . import modelschema
from . import query
from . import ratelaw
#from . import seq
from . import sim
from . import utils
from . import variables
