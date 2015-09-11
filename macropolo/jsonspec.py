# -*- coding: utf-8 -*-

import sys
import os
import json
import unittest


def JSONSpecTestCaseFactory(name, super_class, json_file, mixins=[]):
    """
    Creates a test case class of the given `name` with the given
    `super_class` and `mixins` from JSON read from the given `json_file`.
    The test case class is returned.

    This factory and JSON specification for test cases are meant to
    simplify the creation of test cases and reduce the amount of
    boilerplate Python that needs to be written for such cases.

    Specification for a test case is:
        {
            "macro_name": "<a macro>",
            "arguments": [ ... ],
            "keyword_arguments": { ... },
            "context": {
                "<context variable>": "<value>",
                ...
            }
            "filters": {
                "<filter name>": "<mock value>",
                "<filter name>": ["<first call mock value>",
                                  "<second call mock value>", ...]
            },
            "context_functions": {
                "<function name>": "<mock value>",
                "<function name>": ["<first call mock value>",
                                    "<second call mock value>", ...]
            },
            "templates": {
                "<template file>: {
                    "<macro name>": "<mock value>",
                    "<macro name>"": ["<first call mock value>",
                                    "<second call mock value>", ...]
                }
            },
            "assertions": [
                {
                    "selector": "<css selector>",
                    "index": <1>,
                    "value": "<string contained>",
                    "assertion": "<equal>",
                    "attribute": "<attribute name>",
                "
            ]
        }

    Assertion definitions take a CSS selector, an index in the list of
    matches for that selector (default is 0), the names and mock values
    of any filters or context functions that are used, an assertion,
    a value for comparison (if necessary for the assertion), and, if
    necessary, the attribute on the selected element to compare to.

    "arguments", "keyword_arguments", "filters", "context_functions", 
    and "template" are optional.

    Assertions can be any of the following:
        * equal
        * not equal
        * exis]s
        * in
        * not in

    So a JSON file with multiple testcases (should ideall corrospond
    to a ']ngle template file) would look like this:
        {
            "file": "macros.html",
            "tests": [
                {
                    "macro_name": "my_macro",
                    ...

                 },
                 { ... }
            ]
        }
    """
    # This is a function to convert unicode() objects to str() objects that 
    # are unicode-encoded. This should above output in our template like 
    # "u'foo'" which Jinja2 can't understand.
    def uniconvert(input):
        if isinstance(input, dict):
            return {uniconvert(key): uniconvert(value) 
                    for key, value in input.iteritems()}
        elif isinstance(input, list):
            return [uniconvert(element) for element in input]
        # UGH!
        elif sys.version_info < (3,) and isinstance(input, unicode):
            return input.encode('utf-8')
        else:
            return input

    # This function will return a function that can be assigned as a test 
    # method for a macro with the given name in the given file with the give 
    # test_dict from the JSON spec.
    def create_test_method(macro_file, macro_name, test_dict):
        def test_method(self):
            # Add any context variables to the context
            [self.add_context(k, v) 
                    for k, v in test_dict.get('context', {}).items()]

            # Mock the filters and context functions
            filters = test_dict.get('mock_filters', {})
            [self.mock_filter(f, v) for f, v in filters.items()]
            context_functions = test_dict.get('mock_context_functions', {})
            [self.mock_context_function(f, v) 
                    for f, v in context_functions.items()]
            templates = test_dict.get('templates', {})
            [[self.mock_template_macro(n, m, c) for m, c in d.items()] 
                    for n, d in templates.items()]

            # Render the macro from the macro file with the given
            # arguments
            args = test_dict.get('arguments', [])

            # kwargs can optionally be specified seperately from args
            kwargs = test_dict.get('keyword_arguments', {})

            # If args is a dict it specifies keyword arguments.
            # Otherwise assume it's a list of arguments.
            if isinstance(args, dict):
                kwargs = args
                args = []

            result = self.render_macro(macro_file, macro_name,
                                       *args, **kwargs)

            # Loop over the assertions given for the test and make them.
            for a in test_dict.get('assertions', []):
                # Selector is required, the others here have defaults.
                selector = a['selector']
                index = a.get('index', 0)
                assertion = a.get('assertion', 'exists')
                value = a.get('value')
                attribute = a.get('attribute', '')

                try:
                    self.make_assertion(result, selector, index=index,
                                        value=value, assertion=assertion,
                                        attribute=attribute)
                except AssertionError as e:
                    # Try to provide some more relevent information to the
                    # assertion error, since by default it'll just say the
                    # failure was in make_assertion.
                    assertion_str = ''
                    if value:
                        assertion_str += '"' + value + '" '
                    assertion_str += '"' + assertion + '" "' + \
                        selector + '" selection '

                    e.args += (assertion_str + 
                               'failed in macro ' + macro_name + 
                               ' in ' + macro_file,)
                    raise e

        return test_method

    # Open and read the JSON spec file
    try:
        spec = uniconvert(json.loads(open(json_file).read()))
    except ValueError as e:
        e.args += (' in ' + json_file,)
        raise

    # This will be our new class's dict containing all its methods, etc
    newclass_dict = {}

    # Go through the json_spec dict and create test methods for each test
    macro_file = spec['file']
    for t in spec['tests']:
        # Create the test method and add it to the class dictionary
        macro_name = t['macro_name']
        method_name = 'test_' + str(spec['tests'].index(t)) + macro_name
        test_method = create_test_method(macro_file, macro_name, t)

        if t.get('skip', False):
            test_method = unittest.skip(
                "skipping {}".format(macro_name))(test_method)

        newclass_dict[method_name] = test_method

    # Create and return the new class.
    newclass = type(name, (super_class,), newclass_dict)
    return newclass


def JSONTestCaseLoader(tests_path, super_class, context, recursive=False):
    """
    Load JSON specifications for Jinja2 macro test cases from the given
    `tests_path`, calls `JSONSpecTestCaseFactory()` to create test case
    classes with the given `super_class` from the JSON files, and adds the
    resulting test case classes to the given `context` (i.e. `globals()`).
    """

    json_files = [f for f in os.listdir(tests_path) if f.endswith('.json')]
    for json_file in json_files:
        # Create a camelcased name for the test. This is a minor thing, but I
        # think it's nice.
        name, extension = os.path.splitext(json_file)
        class_name = ''.join(x for x in name.title() if x not in ' _-') \
                + 'TestCase'

        # Get the full path to the file and create a test class
        json_file_path = os.path.join(tests_path, json_file)
        test_class = JSONSpecTestCaseFactory(class_name,
                                             super_class,
                                             json_file_path)
        # Add the test class to globals() so that unittest.main() picks it up
        context[class_name] = test_class
