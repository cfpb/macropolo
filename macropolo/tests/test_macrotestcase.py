# -*- coding: utf-8 -*-

import unittest
import mock

from macropolo import MacroTestCaseMixin

class MacroTestCaseTestCase(unittest.TestCase):
    """
    Tests for the helper/utility methods provided by MacroTestCase
    """

    def test_mock_filter(self):
        """
        Test that mock_filter returns a mock filter with either a single
        return value or a set of side effects.
        """
        # mock_filter() calls the add_filter() method which is defined by
        # environments. Mock that method and we'll get the filter to
        # introspect from that.
        test_case = MacroTestCaseMixin()
        test_case.add_filter = mock.MagicMock(name='add_filter')

        # Test a single consistent return value
        test_case.mock_filter('myfilter', '1')
        call_args = test_case.add_filter.call_args[0]

        # Check that the name is correct and that the return value is
        # consistent.
        self.assertEqual('myfilter', call_args[0])
        self.assertEqual(call_args[1](), '1')
        self.assertEqual(call_args[1](), '1')

        # Test multiple return values
        test_case.mock_filter('multifilter', '2', '3', '4')
        call_args = test_case.add_filter.call_args[0]

        # Check that the name is correct and that the return value is
        # consistent.
        self.assertEqual('multifilter', call_args[0])
        self.assertEqual(call_args[1](), '2')
        self.assertEqual(call_args[1](), '3')
        self.assertEqual(call_args[1](), '4')

    def test_mock_context_function(self):
        """
        Test that mock_context_function returns a mock context function
        with either a single return value or a set of side effects.
        """
        # mock_context_function() calls the add_context() method which
        # is defined by environments. Mock that method and we'll get
        # the filter to introspect from that.
        test_case = MacroTestCaseMixin()
        test_case.add_context = mock.MagicMock(name='add_context')

        # Test a single consistent return value
        test_case.mock_context_function('myfunc', '1')
        call_args = test_case.add_context.call_args[0]

        # Check that the name is correct and that the return value is
        # consistent.
        self.assertEqual('myfunc', call_args[0])
        self.assertEqual(call_args[1](), '1')
        self.assertEqual(call_args[1](), '1')

        # Test multiple return values
        test_case.mock_context_function('multifunc', '2', '3', '4')
        call_args = test_case.add_context.call_args[0]

        # Check that the name is correct and that the return value is
        # consistent.
        self.assertEqual('multifunc', call_args[0])
        self.assertEqual(call_args[1](), '2')
        self.assertEqual(call_args[1](), '3')
        self.assertEqual(call_args[1](), '4')

    def test_make_assertion(self):
        """
        Test that make_assertion makes correct assumptions based on
        input.

        Possible assertions are 'equal', 'not equal', 'exists', 'in',
        'not in'. Things we want to test: element attribute selection,
        each assertion type.
        """
        test_case = MacroTestCaseMixin()

        # We don't need to test BeautifulSoup, so we'll mock
        # result.select(selector). Result can therefore be None.
        mock_result = mock.Mock()
        mock_result.select = mock.Mock()
        mock_result.select.return_value = ['<span class="foo">Test Text</span>',]

        # A mock result with an attribute
        mock_elm = mock.Mock()
        mock_elm.get.return_value = ['foo',]
        mock_result_w_attr = mock.Mock()
        mock_result_w_attr.select = mock.Mock()
        mock_result_w_attr.select.return_value = [mock_elm,]

        mock_empty_result = mock.Mock()
        mock_empty_result.select = mock.Mock()
        mock_empty_result.select.return_value = []

        mock_empty_result_w_attr = mock.Mock()
        mock_empty_result_w_attr.select = mock.Mock()
        mock_empty_result_w_attr.select.return_value = []

        # equals passing
        test_case.make_assertion(mock_result_w_attr, '.foo', index=0,
            value='foo', assertion='equal', attribute='class')
        test_case.make_assertion(mock_result, '.foo', index=0,
            value='<span class="foo">Test Text</span>', assertion='equal')
        test_case.make_assertion(mock_result_w_attr, '.foo', index=0,
            value='foo', assertion='equals', attribute='class')
        test_case.make_assertion(mock_result, '.foo', index=0,
            value='<span class="foo">Test Text</span>', assertion='equals')

        # equals failing
        with self.assertRaises(AssertionError):
            test_case.make_assertion(mock_result_w_attr, '.foo', index=0,
                value='bar', assertion='equal', attribute='class')
            test_case.make_assertion(mock_result, '.foo', index=0,
                value='<span>Test Text</span>', assertion='equal')
            test_case.make_assertion(mock_result_w_attr, '.foo', index=0,
                value='bar', assertion='equals', attribute='class')
            test_case.make_assertion(mock_result, '.foo', index=0,
                value='<span>Test Text</span>', assertion='equals')

        # not equal passing
        test_case.make_assertion(mock_result_w_attr, '.foo', index=0,
            value='foo bar', assertion='not equal', attribute='class')
        test_case.make_assertion(mock_result, '.foo', index=0,
            value='<span class="foo">Test</span>', assertion='not equal')
        test_case.make_assertion(mock_result_w_attr, '.foo', index=0,
            value='foo bar', assertion='not equals', attribute='class')
        test_case.make_assertion(mock_result, '.foo', index=0,
            value='<span class="foo">Test</span>', assertion='not equals')

        # not equal failing
        with self.assertRaises(AssertionError):
            test_case.make_assertion(mock_result_w_attr, '.foo', index=0,
                value='foo', assertion='not equal', attribute='class')
            test_case.make_assertion(mock_result, '.foo', index=0,
                value='<span class="foo">Test Text</span>', assertion='not equal')
            test_case.make_assertion(mock_result_w_attr, '.foo', index=0,
                value='foo', assertion='not equals', attribute='class')
            test_case.make_assertion(mock_result, '.foo', index=0,
                value='<span class="foo">Test Text</span>', assertion='not equals')

        # exists passing
        test_case.make_assertion(mock_result_w_attr, '.foo', index=0,
            assertion='exists', attribute='class')
        test_case.make_assertion(mock_result, '.foo', index=0,
            assertion='exists')

        # exists failing
        with self.assertRaises(AssertionError):
            test_case.make_assertion(mock_empty_result_w_attr, '.foo', index=0,
                assertion='exists', attribute='class')
            test_case.make_assertion(mock_empty_result, '.foo', index=0,
                assertion='exists')

        # in passing
        test_case.make_assertion(mock_result_w_attr, '.foo', index=0,
            value='oo', assertion='in', attribute='class')
        test_case.make_assertion(mock_result, '.foo', index=0,
            value='Test Text', assertion='in')

        # in failing
        with self.assertRaises(AssertionError):
            test_case.make_assertion(mock_result_w_attr, '.foo', index=0,
                value='ar', assertion='in', attribute='class')
            test_case.make_assertion(mock_result, '.foo', index=0,
                value='Something', assertion='in')

        # not in passing
        test_case.make_assertion(mock_result_w_attr, '.foo', index=0,
            value='ar', assertion='not in', attribute='class')
        test_case.make_assertion(mock_result, '.foo', index=0,
            value='Something', assertion='not in')

        # not in failing
        with self.assertRaises(AssertionError):
            test_case.make_assertion(mock_result_w_attr, '.foo', index=0,
                value='oo', assertion='not in', attribute='class')
            test_case.make_assertion(mock_result, '.foo', index=0,
                value='Test Text', assertion='not in')


if __name__ == '__main__':
    unittest.main()

