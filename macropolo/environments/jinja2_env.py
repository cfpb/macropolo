# -*- coding: utf-8 -*-

import os

# We'll use BeautifulSoup to make assertions about the HTML resulting from
# macros
from bs4 import BeautifulSoup

from jinja2 import Environment
from jinja2 import ChoiceLoader, FileSystemLoader, DictLoader


class Jinja2Environment(object):
    """
    Jinja2 macro test environment mixin for `MacroTestCase`
    """

    def setup_environment(self):
        """
        Set up a Jinja2 environment
        """
        search_root = self.search_root()
        search_exceptions = self.search_exceptions()
        self.search_paths = [x[0] for x in os.walk(search_root)
                                if not x[0].startswith('_') or
                                    x[0].startswith('.') or
                                    x[0] in search_exceptions]
        self.filters = {}
        self.context = {}
        self.templates = {}

    def add_filter(self, name, filter):
        """
        Add the given filter to the template environment.
        """
        self.filters[name] = filter

    def add_context(self, name, value):
        """
        Add the given name/value to the template environment context.
        """
        self.context[name] = value

    def add_template_macro(self, name, macro_name, contents):
        """
        Add the given name as a template in the environment with the
        given macro name and contents.
        """
        if name not in self.templates:
            self.templates[name] = {}
        self.templates[name][macro_name] = contents

    def render_macro(self, macro_file, macro, *args, **kwargs):
        """
        Render a given macro with the given arguments and keyword
        arguments. Returns a BeautifulSoup object.

        Internally method will construct a simple string template that
        calls the macro and renders that template and returns the
        result.
        """

        # Add our mock templates to the template dict
        mock_templates = {}
        for name in self.templates:
            macros = []
            for macro_name in self.templates[name]:
                m = """
                    {{% macro {macro_name} %}}{macro_contents}{{% endmacro %}}
                """.format(macro_name=macro_name,
                           macro_contents=self.templates[name][macro_name])
                macros.append(m)
            mock_templates[name] = "\n".join(macros)

        # Build an environment
        fs_loader = FileSystemLoader(self.search_paths)
        mock_template_loader = DictLoader(mock_templates)
        self.env = Environment(loader=ChoiceLoader(
            [mock_template_loader, fs_loader]))
        for f in self.filters:
            self.env.filters[f] = self.filters[f]

        # We need to format args and kwargs as string arguments for the macro.
        # After that we combine them. filter() is used in case one or the other
        # strings is empty, ''.
        str_args = u', '.join(u'{!r}'.format(a) for a in args)
        str_kwargs = u', '.join(u'{!s}={!r}'.format(k, v)
                                for k, v in kwargs.items())
        str_combined = u', '.join(filter(None, [str_args, str_kwargs]))

        # Here is our test template that uses the macro.
        test_template_str = u'''
            {{% import "{macro_file}" as m with context %}}
            {{{{ m.{macro}({args}) }}}}
        '''.format(macro_file=macro_file, macro=macro, args=str_combined)

        test_template = self.env.from_string(test_template_str)

        result = test_template.render(self.context)
        return BeautifulSoup(result, "html.parser")
