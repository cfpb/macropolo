# -*- coding: utf-8 -*-

# Try to import all of our supported template systems

try:
    from .jinja2_env import Jinja2Environment
except ImportError:
    pass

try:
    from .sheer_env import SheerEnvironment
except ImportError:
    pass

