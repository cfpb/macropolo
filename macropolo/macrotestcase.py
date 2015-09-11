# -*- coding: utf-8 -*-

import unittest
import mock


class MacroTestCaseMixin(object):
    """
    The `MacroTestCase` class is intended to capture test cases for
    macros on a modular basis, i.e. you would create one subclass of
    `MacroTestCase` for each template file containing macros. That
    That subclass can then include `test_[macro_name]()` methods that
    test each individual macro.

    render_macro() should return a BeautifulSoup object that you can
    then use CSS selectors on to make assertions. See
    http://www.crummy.com/software/BeautifulSoup/bs4/doc/#css-selectors

    This class requires a templating system environment mixin that
    provides `setup_environment()` that creates the templating
    system environment, `add_filter()` and `add_context()` which add
    filters and context name/values or functions to the template
    environment, and finally `render_macro()` which renders the macro
    using the template system and environment.

    This class is expected to be mixed in with `unittest.TestCase`.
    `MacroTestCase`, defined below, does this for you. It's split up
    for the purpose of testing the helper/utility methods defined below.
    """

    def setup_environment(self):
        """
        Setup the templating system's environment
        """
        raise NotImplementedError("please mixin an environment class")

    def render_macro(self, macro_file, macro, *args, **kwargs):
        """
        Render a given macro with the given arguments and keyword
        arguments. Returns a BeautifulSoup object.
        """
        raise NotImplementedError("please mixin an environment class")

    def add_filter(self, name, filter):
        """
        Add the given filter to the template environment.
        """
        raise NotImplementedError("please mixin an environment class")

    def add_context(self, name, value):
        """
        Add the given name/value to the template environment context.
        """
        raise NotImplementedError("please mixin an environment class")

    def add_template_macro(self, name, macro_name, contents):
        """
        Add the given name as a template in the environment with the
        given macro name and contents.
        """
        raise NotImplementedError("please mixin an environment class")

    def search_root(self):
        """
        Return the root of the search path for templates.
        """
        raise NotImplementedError("please provide a search_root() in "
                                  "your MacroTestCase subclass")

    def search_exceptions(self):
        """
        Return a list of a subdirectory names that should not be searched
        for templates.
        """
        raise NotImplementedError("please provide a self.search_exceptions() "
                                  "in your MacroTestCase subclass")

    def setUp(self):
        self.setup_environment()

    def mock_filter(self, filter, *values):
        """
        Mock a template filter. This will create a mock function for the
        filter that will return either a single value or will return
        each of the given values in turn if there are more than one.

        Sheer filters you might want to mock:
            selected_filters_for_field
            is_filter_selected

        """
        mock_filter = mock.Mock()

        if len(values) > 1:
            mock_filter.side_effect = values
        elif len(values) == 1:
            mock_filter.return_value = values[0]

        self.add_filter(filter, mock_filter)

    def mock_context_function(self, func, *values):
        """
        Mock a context function. This will create a mock function that
        will return either a single value or will return each of the
        given values in turn if there are more than one.

        Sheer context functions you might want to mock:
            queries
            more_like_this
            get_document
        """
        mock_func = mock.Mock()

        if len(values) > 1:
            mock_func.side_effect = values
        elif len(values) == 1:
            mock_func.return_value = values[0]

        self.add_context(func, mock_func)

    def mock_template_macro(self, name, macro_name, contents):
        """
        Mock calls to a macro in another template.

        Implementation details may varry between templating systems.
        """
        self.add_template_macro(name, macro_name, contents)

    def make_assertion(self, result, selector, index=0,
                       value=None, assertion='exists', attribute=''):
        """
        Make an assertion based on the BeautifulSoup result object.

        This method will find the given CSS selector, and make the given
        assertion about the attribute of selector's match at the given
        index. If the assertion requires a value to compare to, it should
        be given. If no attribute is given the assertion is made about
        the entire match.
        """

        selection = result.select(selector)

        # Get the value we're making assertions about. It's either the
        # selection itself or the value of the given attribute on the
        # selection.
        try:
            selection_value = selection[index]
            if attribute:
                try:
                    selection_value = selection[index].get(attribute)[0]
                except TypeError:
                    raise AssertionError("attribute '%s' does not exist "
                                         "or is empty" % attribute)
        except IndexError:
            selection_value = ''

        if assertion == 'equal' or assertion == 'equals':
            assert value == selection_value
        elif assertion == 'not equal' or assertion == 'not equals':
            assert value != selection_value
        elif assertion == 'exists':
            assert selection_value
        elif assertion == 'in':
            assert value in selection_value
        elif assertion == 'not in':
            assert value not in selection_value
        else:
            raise AssertionError("assertion '%s' does not exist" % assertion)


class MacroTestCase(MacroTestCaseMixin, unittest.TestCase):
    """
    """
    pass
