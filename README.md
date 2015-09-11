# Macro Polo

[![Build Status](https://travis-ci.org/cfpb/macropolo.png)](https://travis-ci.org/cfpb/macropolo)

- [Why Macro Polo? Unit Testing vs Functional Testing](#why-macro-polo-unit-testing-vs-functional-testing)
- [Requirements](#requirements)
- [Installation](#installation)
- [Testing Macro Polo](#testing-macro-polo)
- [Using Macro Polo](#using-macro-polo)
    - [Quickstart](#quickstart)
    - [Creating a Base TestCase Class](#creating-a-base-testcase-class)
    - [Defining Tests in JSON](#defining-tests-in-json)
    - [Defining Tests in Python](#defining-tests-in-python)
    - [Running Tests](#running-tests)
- [API](#api)
    - [`MacroTestCase`](#macrotestcase)
    - [Template Environment Mixins](#template-environment-mixins)
    - [JSON Specification Functions](#json-specification-functions)
- [Licensing](#licensing)


Macro Polo is a Python library for unit testing template macros created 
using popular Python templating systems.

Templating systems/environments currently supported:

- [Jinja2](http://jinja.pocoo.org/)
- Jinja2 Templates served via [Sheer](https://github.com/cfpb/sheer)

**Status:** Proof of concept

## Why Macro Polo? Unit Testing vs Functional Testing

Macro Polo is designed for unit testing template macros. Macro Polo 
is meant to make it easier to express tests of the resulting HTML of 
individual template macros (units) within a specific context or with
specific inputs. Unit testing macros tests them individually in 
isolation. 

If you're looking at a template and want to test browser-related 
behavior that occurs when interacting with that template's resulting 
HTML, you want to investigate functional testing tools and frameworks.

## Requirements

Requirements can be satisfied with `pip`:

```shell
$ pip install -r requirements.txt
```

- [BeautifulSoup 4](http://www.crummy.com/software/BeautifulSoup/) for
  handling the HTML resulting from template rendering
- [Python mock](http://www.voidspace.org.uk/python/mock/) for mocking
  template filters and context (and unit testing Macro Polo itself)

Template Systems/Environments:

- [Jinja2](http://jinja.pocoo.org/)
- [Sheer](https://github.com/cfpb/sheer)

These are not installed by `pip`. It is expected that if you are using
these template environments you have them installed already. If not,
their respective [environment mixins](#template-environment-mixins) will 
not be available.

## Installation

To clone and install Macro Polo locally in an existing Python 
[`virtualenv`](https://virtualenv.pypa.io/en/latest/):

```shell
$ git clone https://github.com/cfpb/macropolo
$ pip install -e macropolo
```

Note: this installs Macro Polo in 'editable' mode. This means that any
updates pulled into the git clone will be 'live' without running `pip`
again.

Macro Polo can also be installed directly from Github:

```shell
$ pip install git+https://github.com/cfpb/macropolo
```

## Testing Macro Polo

Macro Polo's own unit tests can be run from the root of the repository:

```shell
$ python setup.py test
``` 

If you would prefer to use [nose](https://nose.readthedocs.org/en/latest/):

```shell
$ pip install nose
```

Then you can run the tests:

```shell
$ nosetests macropolo
```

## Using Macro Polo

### Quickstart

Create a Python file with the rest of your test suite, such as
`test_templates.py`. This file will need to define a 
[base test case](#creating-a-base-testcase-class),
load template tests from JSON, and (optionally) use Python's
`unittest.main()` to [run the tests](#running-tests):

```python
from macropolo import MacroTestCase, Jinja2Environment
from macropolo import JSONTestCaseLoader

class MyBaseTestCase(Jinja2Environment, MacroTestCase):
    """
    A MacroTestCase subclass for my Jinja2 Templates.
    """

    def search_root(self):
        """
        Return the root of the search path for templates.
        """
        # If the tests live under 'site_root/tests'...
        root_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ),
                                                os.pardir))
        return root_dir

    def search_exceptions(self):
        """
        Return a list of a subdirectory names that should not be searched
        for templates.
        """
        return ['tests',]

# Create MyTestCase subclasses for all JSON tests and add them to the
# module's global context.
tests_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'template_tests'))
JSONTestCaseLoader(tests_path, MyBaseTestCase, globals())

# Run the tests if we're executed
if __name__ == '__main__':
    unittest.main()
```

Then create your [JSON test specifications](#defining-tests-in-json) in
the `template_tests` subdirectory of `tests`.

### Creating a Base TestCase Class

Test Case classes should inherit from a
[template environment mixin](#template-environment-mixins), the
[`MacroTestCase`](#macrotestcase) class, and should provide the 
following methods:

#### `search_root()`

Return the root of the search path for templates.

#### `search_exceptions()`

Return a list of a subdirectory names that should not be searched
for templates.

For Example:

```python
from macropolo import MacroTestCase, Jinja2Environment

class MyBaseTestCase(Jinja2Environment, MacroTestCase):
    """
    A MacroTestCase subclass for my Jinja2 Templates.
    """

    def search_root(self):
        """
        Return the root of the search path for templates.
        """
        # If the tests live under 'site_root/tests'...
        root_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ),
                                                os.pardir))
        return root_dir

    def search_exceptions(self):
        """
        Return a list of a subdirectory names that should not be searched
        for templates.
        """
        return ['tests',]
```


### Defining Tests in JSON

To reduce the amount of boilerplate Python that needs to be written for
macro unit tests, unit tests can be written in JSON.

For each template file that defines macros, a single JSON should be
created that would look like this:

```json
{
    "file": "macros.html",
    "tests": [
        {
            "macro_name": "my_macro",
            ...
        },
        { ... },
    ]
}
```

**`file`** is the template file. The test environment uses the same
mechanism that Sheer uses to lookup template files, so the same file
specification that's used within templates that use the macros.

**`tests`** is a list of individual test case specifications. These
corrospond to a single macro.

The specification for a test case for an individual macro looks like
this:

```json
{
    "macro_name": "<a macro>",
    "skip": <true or false>,
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
        "<template file>": {
            "<macro name>(<arguments>)": "<mock value>",
            "<macro name>()": ["<first call mock value>",
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
```

**`macro_name`** is simply the name of the macro within the file in which it
is defined.

**`skip`**, if true, will skip the macro test. This is optional.

**`arguments`** is a list of arguments to pass to the macro in the order
they are given. Can be either a list or a JSON object of keys/values; if 
it is a JSON object of keys/values, it is presumed to be keyword 
arguments. This is optional.

**`keyword_arguments`** is an object containing key/value arguments to pass
to the macro if it requires keyword arguments. This is optional.

**`context`** is an object containing names of context variables to add
to the template's context and values to assign to those variables.

**`filters`** is an object that is used to mock template system filters. 
It contains the name of the filter to be mocked and the value that should
be returned when that filter is used. The value can also be a list, in
which case the order of the list will corropsond to the order in which
the filter is called, i.e. if you want the filter to return `1` the
first time it is called, but `2` the second time, the value would be
`[1, 2]`. This is optional.

*Note:* Here are some Sheer filters you may want to consider mocking:

- `selected_filters_for_field`
- `is_filter_selected`

**`context_functions`** is an object that is used to mock template 
context functions. It works the same way that `filters` does above, 
with the values either being a return value for all calls or a list of 
return values for each call. This is optional.

*Note:* Here are some Sheer context functions you may want to consider
mocking:

- `queries`
- `more_like_this`
- `get_document`

**`templates`** is an object that is used to mock included template
macros called from within the macro being tested. It works the same 
way that `filters` and `context_functions` do above, with the values 
either being a return value for all calls or a list of return values 
for each call.  The `<macro name>` should include parenthesis and any 
arguments the template's macro takes. This will override *the entire 
`<template file>`*, so make sure to mock all of its macros.  This is 
optional.

**`assertions`** defines the assertions to make about the result of
rendering the macro. Assertion definitions take a CSS `selector`, an 
`index` in the list of matches for that selector (default is `0`), an 
`assertion` to make about the selected element or its `attribute` (if 
given), and a `value` for comparison (if necessary for the assertion).

The `assertion` can be any of the following:

- `equal` or `equals`
- `not equal` or `not equals`
- `exists`
- `in`
- `not in`

Multiple test cases can be defined for the same macro, to test different
behavior with different inputs, filter or context funciton output.

### Defining Tests in Python

If there is a more complex scenario you would like to test that cannot
be described by the JSON specification format, you can create a test
case in Python. 

```python
class MyMacrosTestCase(MyBaseTestCase):
    def test_a_macro(self):
        self.mock_filter(...)
        self.mock_context_function(...)
        result = self.render_macro('mymacros.html', 'amacro')
        assert 'something' in result.select('.css-selector')[0]
````

### Running Tests

Using the [`MyBaseTestCase` class defined above](#creating-a-base-testcase-class) 
and loading tests [defined in JSON files](#defining-tests-in-json), the
JSON files must be loaded into into a Python context. 

For example, in a file called `template_tests.py`:

```python
from macropolo import JSONTestCaseLoader

# Create MyTestCase subclasses for all JSON tests and add them to the
# module's global context.
tests_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'template_tests'))
JSONTestCaseLoader(tests_path, MyBaseTestCase, globals())

# Run the tests if we're executed
if __name__ == '__main__':
    unittest.main()
```

From there the file can be run as-is:

```shell
$ python template_tests.py
```

Or it can be run using other Python test runners like [nose](https://nose.readthedocs.org/en/latest/):

```shell
$ pip install nose
$ nosetests 
```

Or [py.test](http://pytest.org/latest/)

```shell
$ pip install pytest
$ py.test
```

## API

### `MacroTestCase`

The `MacroTestCase` class is intended to capture test cases for
macros on a modular basis, i.e. you would create one subclass of
`MacroTestCase` for each template file containing macros. That
subclass can then include `test_[macro_name]()` methods that
test each individual macro.

This class requires a 
[templating system environment mixin](#template-environment-mixins) 
that provides `setup_environment()` that creates the templating
system environment, `add_filter()` and `add_context()` which add
filters and context name/values or functions to the template
environment, and finally `render_macro()` which renders the macro
using the template system and environment.

`MacroTestCase` provides the following convenience methods:

#### `mock_filter(filter, **values)`

Mock a template filter. This will create a mock function for the
filter that will return either a single value, or will return
each of the given values in turn if there are more than one.

#### `mock_context_function(func, **values)`

Mock a context function. This will create a mock function that
will return either a single value, or will return each of the
given values in turn if there are more than one.

#### `make_assertion(result, selector, index=0, value=None, assertion='exists', attribute='')`

Make an assertion based on the BeautifulSoup result object.

This method will find the given CSS selector, and make the given
assertion about the attribute of selector's match at the given
index. If the assertion requires a value to compare to, it should
be given. If no attribute is given the assertion is made about
the entire match.


### Template Environment Mixins

Template System environment mixin classes should provide four methods:

#### `setup_environment()`

This method should setup the templating system's environment.

#### `render_macro(macro_file, macro, *args, **kwargs)`

Render a given macro with the given arguments and keyword
arguments. Should return a BeautifulSoup object.

#### `add_filter(name, filter)`

Add the given filter to the template environment.

#### `add_context(name, value)`

Add the given name/value to the template environment context.

### JSON Specification Functions 

#### `JSONTestCaseLoader(tests_path, super_class, context)`

Load JSON specifications for Jinja2 macro test cases from the given
`tests_path`, calls `JSONSpecTestCaseFactory()` to create test case
classes with the given `super_class` from the JSON files, and adds the
resulting test case classes to the given `context` (i.e. `globals()`).

#### `JSONSpecTestCaseFactory(name, super_class, json_file, mixins=[])`

Creates a test case class of the given `name` with the given
`super_class` and `mixins` from JSON read from the given `json_file`.
The test case class is returned.

## Licensing 

Public Domain/CC0 1.0

1. [Terms](TERMS.md)
2. [License](LICENSE)
3. [CFPB Source Code Policy](https://github.com/cfpb/source-code-policy/)


