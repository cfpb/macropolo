# -*- coding: utf-8 -*-

import unittest
import mock
from io import StringIO

from macropolo import MacroTestCaseMixin
from macropolo.environments import Jinja2Environment

# This is a TestCase-like class based on Jinja2Environment and
# MacroTestCaseMixin to use to test specific macros. This doesn't use
# MacroTestCase itself to avoid confusing Python's unittest module.
class Jinja2MacroTestCase(Jinja2Environment, MacroTestCaseMixin):
    """
    A subclass to test Jinja2Environment.
    """

    def search_root(self):
        return "."

    def search_exceptions(self):
        return None


class Jinja2EnvironmentTestCase(unittest.TestCase):
    """
    Tests for the Jinja2Environment for macro test cases
    """

    @mock.patch('os.walk')
    @mock.patch('jinja2.FileSystemLoader.get_source')
    def test_basic_macro(self, mock_loader_get_source, mock_os_walk):
        """ 
        Test a basic Jinja2 macro
        """

        # The Jinja2 macro to test.
        macro_string = """
            {% macro test_macro() %}
                Hello World!
            {% endmacro %}
        """

        # Mock os.walk, which Jinja2Environment uses to generate a list
        # of search paths.
        mock_os_walk.return_value = [
                    ('/', (), 'macro.html')
                ]
        # Mock FileSystemLoader.get_source to return our macro_string
        mock_loader_get_source.return_value = \
                (macro_string, 'macro.html', None)

        # Initialize the test case
        test_case = Jinja2MacroTestCase()
        test_case.setUp()

        # Render the template
        # test_case.mock_filter()
        # test_case.mock_context()
        # test_case.mock_context_function()
        result = test_case.render_macro('macro.html', 'test_macro')
        assert 'Hello World' in result.text

    @mock.patch('os.walk')
    @mock.patch('jinja2.FileSystemLoader.get_source')
    def test_macro_with_filter(self, mock_loader_get_source, mock_os_walk):
        """ 
        Test a Jinja2 macro with a filter
        """

        # The Jinja2 macro to test.
        macro_string = """
            {% macro test_macro() %}
                Hello {{ "America"|internationalize }}!
            {% endmacro %}
        """

        # Mock os.walk, which Jinja2Environment uses to generate a list
        # of search paths.
        mock_os_walk.return_value = [
                    ('/', (), 'macro.html')
                ]
        # Mock FileSystemLoader.get_source to return our macro_string
        mock_loader_get_source.return_value = \
                (macro_string, 'macro.html', None)

        # Initialize the test case
        test_case = Jinja2MacroTestCase()
        test_case.setUp()

        # Create a mock filter
        test_case.mock_filter('internationalize', 'World')

        result = test_case.render_macro('macro.html', 'test_macro')
        assert 'Hello World' in result.text

    @mock.patch('os.walk')
    @mock.patch('jinja2.FileSystemLoader.get_source')
    def test_macro_with_context(self, mock_loader_get_source, mock_os_walk):
        """ 
        Test a Jinja2 macro with context 
        """

        # The Jinja2 macro to test.
        macro_string = """
            {% macro test_macro() %}
                Hello {{ who }} !
            {% endmacro %}
        """

        # Mock os.walk, which Jinja2Environment uses to generate a list
        # of search paths.
        mock_os_walk.return_value = [
                    ('/', (), 'macro.html')
                ]
        # Mock FileSystemLoader.get_source to return our macro_string
        mock_loader_get_source.return_value = \
                (macro_string, 'macro.html', None)

        # Initialize the test case
        test_case = Jinja2MacroTestCase()
        test_case.setUp()

        # Add a value to the context
        test_case.add_context('who', 'World')

        result = test_case.render_macro('macro.html', 'test_macro')
        assert 'Hello World' in result.text

    @mock.patch('os.walk')
    @mock.patch('jinja2.FileSystemLoader.get_source')
    def test_macro_with_context_func(self, mock_loader_get_source, mock_os_walk):
        """ 
        Test a Jinja2 macro with context 
        """
        # Test a simple context function
        macro_string = """
            {% macro test_macro() %}
                Hello {{ who() }}!
            {% endmacro %}
        """
    
        # Test calling a macro from another file
        namespaced_other_macro_macro_string = """
            {% macro test_macro() %}
                {% import "somefile" as somefile with context %}
                Hello {{ somefile.somemacro() }}!
            {% endmacro %}
        """
        
        # Mock os.walk, which Jinja2Environment uses to generate a list
        # of search paths.
        mock_os_walk.return_value = [
                    ('/', (), 'macro.html')
                ]
        # Mock FileSystemLoader.get_source to return our macro_string
        mock_loader_get_source.return_value = \
                (macro_string, 'macro.html', None)

        # Initialize the test case
        test_case = Jinja2MacroTestCase()
        test_case.setUp()

        # Add a context function value
        test_case.mock_context_function('who', 'America')

        result = test_case.render_macro('macro.html', 'test_macro')
        assert 'Hello America' in result.text

    @mock.patch('os.walk')
    @mock.patch('jinja2.FileSystemLoader.get_source')
    def test_macro_with_another_template(self, mock_loader_get_source, mock_os_walk):
        """
        Test a Jinja2 Macro that loads another macro.
        """

        # Test a simple context function
        macro_string = """
            {% macro test_macro() %}
                {% import "who.html" as who with context %}
                Hello {{who.america() }} & {{ who.international() }}!
            {% endmacro %}
        """
    
        # Mock os.walk, which Jinja2Environment uses to generate a list
        # of search paths.
        mock_os_walk.return_value = [
                    ('/', (), 'macro.html')
                ]
        # Mock FileSystemLoader.get_source to return our macro_string
        mock_loader_get_source.return_value = \
                (macro_string, 'macro.html', None)

        # Initialize the test case
        test_case = Jinja2MacroTestCase()
        test_case.setUp()

        # Mock a template macro.
        test_case.mock_template_macro("who.html", "america()", "America")
        test_case.mock_template_macro("who.html", "international()", "World")

        result = test_case.render_macro('macro.html', 'test_macro')
        assert 'America' in result.text
        assert 'World' in result.text


