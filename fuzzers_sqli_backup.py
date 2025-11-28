from django.core.exceptions import (
    ValidationError,
    SuspiciousFileOperation,
)

from django.utils import text
from django.utils.http import (
    base36_to_int,
    escape_leading_slashes,
    int_to_base36,
    url_has_allowed_host_and_scheme,
    parse_etags,
    parse_http_date,
    quote_etag,
    urlencode,
    urlsafe_base64_decode,
    urlsafe_base64_encode,
)
from django.utils.html import (
    conditional_escape,
    escape,
    escapejs,
    # format_html,
    # html_safe,
    json_script,
    linebreaks,
    smart_urlquote,
    strip_spaces_between_tags,
    strip_tags,
    urlize,
)
from django.utils.ipv6 import clean_ipv6_address, is_valid_ipv6_address
import datetime
from django.utils import feedgenerator
from django.utils.encoding import (
    DjangoUnicodeDecodeError,
    escape_uri_path,
    filepath_to_uri,
    iri_to_uri,
    smart_str,
    uri_to_iri,
)
from django import forms
from django.conf import settings

# These are used for the sql fuzzing...

from django.db import models, connection
from django.db.utils import ProgrammingError
from django.db.models import Value, F # For the test stuff...

# For some exceptions...

from django.core.exceptions import EmptyResultSet, FieldError, FullResultSet

import random

import django

import inspect # Needed for dynamic stuff

# import .expression_models as expression_models
# settings.configure() #  Don't use the default stuff here.
# Instead use these settings...

settings.configure(
    DEBUG=True,
    SECRET_KEY='injectiontest',
    INSTALLED_APPS=['fuzzer_project'],
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',  # In-memory DB
        }
    }
)

django.setup()

from expression_models import * # Imports all of the shit.

def setup_models():
    # Sets up the models
    with connection.schema_editor() as schema_editor:
        for name in expression_model_names: # For each name
            assert name in globals() # Should be available
            schema_editor.create_model(globals()[name]) # Taken from expression_models
    # Extract model classes from the module
    print("[+] Succesfully setup the fuzzing models!!!")

setup_models()

# Here are the fuzzer targets

'''
# from test_queryset_values.py:

    def test_values_expression_alias_sql_injection(self):
        crafted_alias = """injected_name" from "expressions_company"; --"""
        msg = (
            "Column aliases cannot contain whitespace characters, quotation marks, "
            "semicolons, or SQL comments."
        )
        with self.assertRaisesMessage(ValueError, msg):
            Company.objects.values(**{crafted_alias: F("ceo__salary")})

    @skipUnlessDBFeature("supports_json_field")
    def test_values_expression_alias_sql_injection_json_field(self):
        crafted_alias = """injected_name" from "expressions_company"; --"""
        msg = (
            "Column aliases cannot contain whitespace characters, quotation marks, "
            "semicolons, or SQL comments."
        )
        with self.assertRaisesMessage(ValueError, msg):
            JSONFieldModel.objects.values(f"data__{crafted_alias}")

        with self.assertRaisesMessage(ValueError, msg):
            JSONFieldModel.objects.values_list(f"data__{crafted_alias}")

'''

def target_queryset_alias(test_string):
    # Now try to fuzz for the thing...
    # Company.objects.values(**{crafted_alias: F("ceo__salary")})
    # print("Here is the passed string: "+str(test_string))
    res = Company.objects.values(**{test_string: F("ceo__salary")})# .exists()
    # print("Result: "+str(res))
    return res

def target_queryset_alias_json_field1(test_string):
    res = JSONFieldModel.objects.values(f"data__{test_string}")
    return res

def target_queryset_alias_json_field2(test_string):
    res = JSONFieldModel.objects.values_list(f"data__{test_string}")
    return res

# All known expression models
expression_model_names = [
    "Manager", "Employee", "RemoteEmployee", "Company", "Number", "Experiment",
    "Result", "Time", "SimulationRun", "UUIDPK", "UUID", "JSONFieldModel",
    "Author", "Publisher", "Book", "Store", "Employee_aggregation", "DTModel"
]

# The interesting ORM methods to target
interesting_methods = ["filter", "values", "values_list", "annotate", "aggregate", "exclude"]

def dynamic_fuzz_target(test_string):
    # print("poopoo")
    # Random model and ORM method
    if len(test_string) <= 2:
        return
    model_name = expression_model_names[ord(test_string[0]) % len(expression_model_names)]
    method_name = interesting_methods[ord(test_string[1]) % len(interesting_methods)]
    test_string = test_string[2:] # Cut the thing...
    
    # Get the model class from app registry
    # Model = apps.get_model('app', model_name)
    print("Model: "+str(model_name))
    assert model_name in globals()
    Model = globals()[model_name]
    manager = Model.objects

    # Check if method exists and is callable
    if not hasattr(manager, method_name):
        print(f"{method_name} not available on {model_name}")
        return
    
    method = getattr(manager, method_name)
    if not callable(method):
        print(f"{method_name} is not callable on {model_name}")
        return
    print("Method name: "+str(method_name))
    try:
        # Generate test input
        if method_name in ("values", "values_list"):
            res = method(f"{test_string}")
        elif method_name in ("filter", "exclude"):
            res = method(**{f"{test_string}": F("id")})
        elif method_name == "annotate":
            res = method(**{f"{test_string}": F("id")})
        elif method_name == "aggregate":
            # These expect aggregations like Sum('field'), so not fuzzing-friendly; skip or simulate
            return
        else:
            return

        # Evaluate the queryset to trigger potential DB errors
        list(res)  # force evaluation
    except Exception as e:
        print("Exception caught:", type(e).__name__, str(e))
        raise  # or log it for crash deduplication






# Test functions list

test_funcs = [target_queryset_alias, target_queryset_alias_json_field1, target_queryset_alias_json_field2, dynamic_fuzz_target]

# Now here is the main fuzz function...

def fuzz_sqli(data: bytes): # Fuzz for SQL injection
    if len(data) < 2:
        return
    test_index = data[0] % len(test_funcs)
    assert isinstance(test_index, int)
    try:
        test_string = data.decode("utf-8") # Decode as utf-8
        print("Here is the string: "+str(test_string))
        if "\x00" in test_string: # Ban null bytes
            return
    except:
        return # Just return if invalid utf-8
    # Now try to pass the thing
    func = test_funcs[test_index]
    try:
        func(test_string) # Call target function
    except (ValueError, FieldError):
        # print("valueerror!!!")
        return
    return # Return

def test0():
    print("Called fuzzers_sqli.py as main script. This is only for testing purposes!!!!!!!!!!!!")
    test_func_index = 0 # target_queryset_alias
    test_string = "sampletext\"fefe--dedef[[[[\"\"''''']]]]".encode("utf-8") # Encode as bytes.
    assert isinstance(test_string, bytes)
    test_data = bytes([test_func_index] + list(test_string)) # Append the function index.
    fuzz_sqli(test_data) # Test the fuzz stuff
    return

def test1():
    print("Called fuzzers_sqli.py as main script. This is only for testing purposes!!!!!!!!!!!!")
    test_func_index = 3 # target_queryset_alias
    test_string = "sampletext\"fefe--dedef[[[[\"\"''''']]]]".encode("utf-8") # Encode as bytes.
    assert isinstance(test_string, bytes)
    test_data = bytes([test_func_index] + list(test_string)) # Append the function index.
    fuzz_sqli(test_data) # Test the fuzz stuff
    return

def test():
    test0()
    test1()

if __name__=="__main__": # Only for testing.
    test()
    exit(0)
