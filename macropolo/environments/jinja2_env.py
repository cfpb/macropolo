# -*- coding: utf-8 -*-

import os

# We'll use BeautifulSoup to make assertions about the HTML resulting from
# macros
from bs4 import BeautifulSoup

from jinja2 import Environment, FileSystemLoader

class Jinja2Environment(object):
    """
    Jinja2 marco test environment mixin for `MacroTestCase`
    """

    def setup_environment(self):
        """
        Set up a Jinja2 environment
        """
        search_root = self.search_root()
        search_exceptions = self.search_exceptions()
        search_paths = [x[0] for x in os.walk(search_root)
                        if not x[0].startswith('_') or x[0].startswith('.') or
                            x[0] in search_exceptions]

        self.env = Environment(loader=FileSystemLoader(search_paths))

        # This is our template context. You can use mock_context_function()
        # below to mock context functions, or you can add values to this
        # dictionary directly.
        self.context = {}


    def add_filter(self, name, filter):
        """
        Add the given filter to the template environment.
        """
        self.env.filters[name] = filter


    def add_context(self, name, value):
        """
        Add the given name/value to the template environment context.
        """
        self.context[name] = value


    def render_macro(self, macro_file, macro, *args, **kwargs):
        """
        Render a given macro with the given arguments and keyword
        arguments. Returns a BeautifulSoup object.

        Internally method will construct a simple string template that
        calls the macro and renders that template and returns the
        result.
        """
        # We need to format args and kwargs as string arguments for the macro.
        # After that we combine them. filter() is used in case one or the other
        # strings is empty, ''.
        str_args = u', '.join('%r'.encode('utf-8') % a for a in args).encode('utf-8')
        str_kwargs = u', '.join('%s=%r' % x for x in kwargs.iteritems())
        str_combined = u', '.join(filter(None, [str_args, str_kwargs]))

        # Here is our test template that uses the macro.
        test_template_str = u'''{%% import "%s" as macro_file %%}{{ macro_file.%s(%s) }}''' % (macro_file, macro, str_combined)
        test_template = self.env.from_string(test_template_str)

        result = test_template.render(self.context)
        return BeautifulSoup(result)


