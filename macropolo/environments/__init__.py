# -*- coding: utf-8 -*-
# flake8: noqa

__all__ = []

# Try to import all of our supported template systems
try:
    from .jinja2_env import Jinja2Environment
    __all__.append('Jinja2Environment')
except ImportError:
    pass

try:
    from .sheer_env import SheerEnvironment
    __all__.append('SheerEnvironment')
except ImportError:
    pass

