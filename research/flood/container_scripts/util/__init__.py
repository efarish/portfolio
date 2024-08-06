# __init__.py
import importlib
import sys

from .DataUtil import DataUtil

importlib.reload(sys.modules['util.DataUtil'])
importlib.reload(sys.modules['util'])

# This line prevents having to reload the package twice.
from .DataUtil import DataUtil