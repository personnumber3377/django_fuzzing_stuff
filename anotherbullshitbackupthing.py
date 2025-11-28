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
from django.db.models import Value, F, Avg # For the test stuff...

# For some exceptions...

from django.core.exceptions import EmptyResultSet, FieldError, FullResultSet# , NotSupportedError # Not in exceptions, because reasons.

from django.db.utils import NotSupportedError, OperationalError

# These next things is for the other thing

from django.http.response import JsonResponse
from datetime import datetime
from django.db.models.functions import Extract, Trunc
from django.db.models import DateTimeField
# from vuln.models import Experiment
from django.core import serializers

from django.utils import timezone # For some stuff

# django.db.utils.OperationalError

# from django.db.utils.OperationalError

import random

import django

import inspect # Needed for dynamic stuff

# import .expression_models as expression_models
# settings.configure() #  Don't use the default stuff here.
# Instead use these settings...

'''
settings.configure(
    DEBUG=False, # Was originally "True,"
    SECRET_KEY='injectiontest',
    INSTALLED_APPS=['app', 'fuzzer_project'], # INSTALLED_APPS=['fuzzer_project'], # Also include 'app' here...
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',  # In-memory DB
        }
    }
)
'''

settings.configure(
    DEBUG=True, # Was originally "True,"
    SECRET_KEY='injectiontest',
    INSTALLED_APPS=['app', 'fuzzer_project'], # INSTALLED_APPS=['fuzzer_project'], # Also include 'app' here...
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'pooopoo',  # In-memory DB
        }
    }
)

django.setup()

# Migration bullshit

from django.core.management import call_command
from django.conf import settings

# Create migrations
call_command('makemigrations', 'app')

# Apply migrations
call_command('migrate')

from app.models import * # Models

'''
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
'''


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
    list(res)

def target_queryset_alias_json_field1(test_string):
    res = JSONFieldModel.objects.values(f"data__{test_string}")
    list(res)

def target_queryset_alias_json_field2(test_string):
    res = JSONFieldModel.objects.values_list(f"data__{test_string}")
    list(res)

# All known expression models
expression_model_names = [
    "Manager", "Employee", "RemoteEmployee", "Company", "Number", "Experiment",
    "Result", "Time", "SimulationRun", "UUIDPK", "UUID", "JSONFieldModel",
    "Author", "Publisher", "Book", "Store", "Employee_aggregation", "DTModel"
]

# The interesting ORM methods to target
interesting_methods = ["filter", "values", "values_list", "annotate", "aggregate", "exclude", "explain"]

'''
def fuzz_queryset_explain(test_string):
    try:
        qs = Tag.objects.filter(name="test")

        # Try to craft malicious-looking options
        # The test_string will be the key of a kwarg passed to `.explain()`
        options = {test_string: True}

        # Evaluate the `.explain()` call with potentially dangerous options
        qs.explain(**options)
    except ValueError as e:
        print(f"Caught expected ValueError: {e}")
    except Exception as e:
        print(f"Caught unexpected {type(e).__name__}: {e}")
'''

# These functions are taken from 

def vuln_extract(test_string):
    payload = test_string
    start = datetime(2015, 6, 15)
    end = datetime(2015, 7, 2)
    Experiment_thing.objects.create(
        start_datetime=start, start_date=start.date(),
        end_datetime=end, end_date=end.date())
    # Experiment_thing.objects.filter
    experiments = DTModel.objects.filter(start_datetime__year=Extract('end_datetime', "day' FROM start_datetime)) "+str(payload)))
    # experiments = DTModel.objects.filter(start_datetime__year=Extract('end_datetime', "day' FROM start_datetime)) "+str(payload)))
    # experiments = Experiment_thing.objects.filter(start_datetime__year=Extract('end_datetime', payload))
    return JsonResponse({"res": serializers.serialize("json", experiments)})

# /trunc/?kind=xxx
def vuln_trunc(test_string):
    print("Here is the test_string: "+str(test_string))
    payload = test_string
    start = datetime(2015, 6, 15)
    end = datetime(2015, 7, 2)
    Experiment_thing.objects.create(
        start_datetime=start, start_date=start.date(),
        end_datetime=end, end_date=end.date())
    # year', start_datetime))
    # DTModel.objects.filter
    # Experiment_thing.objects.filter
    # experiments = DTModel.objects.filter(start_datetime__date=Trunc('start_datetime', "year', start_datetime)) "+str(payload)))
    # experiments = Experiment_thing.objects.filter(start_datetime__date=Trunc('start_datetime', payload))
    # res = JsonResponse({"res": serializers.serialize("json", experiments)})
    '''
    res = DTModel.objects.filter(
                start_datetime__date=Trunc(
                    "start_datetime",
                    "year', start_datetime)) OR 1=1;--",
                )
            ).exists()
    '''

    res = DTModel.objects.filter(start_datetime__date=Trunc('start_datetime', str(payload))).exists()
    return res

vuln_stuff = [vuln_extract, vuln_trunc]

def test_other_functions(test_string):
    if len(test_string) <= 1:
        return
    vuln_func_thing = vuln_stuff[ord(test_string[0]) % len(vuln_stuff)]
    test_string = test_string[1:]
    # Now call the thing...
    vuln_func_thing(test_string) # Call that shit.
    return

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
    # print("Model: "+str(model_name))
    assert model_name in globals()
    Model = globals()[model_name]
    manager = Model.objects
    # Print lookups

    # lookups = Model.get_lookups()
    # print("Here are the lookups: "+str(list(lookups.keys())))
    # Check if method exists and is callable
    if not hasattr(manager, method_name):
        # print(f"{method_name} not available on {model_name}")
        return
    
    method = getattr(manager, method_name)
    if not callable(method):
        # print(f"{method_name} is not callable on {model_name}")
        return
    # print("Method name: "+str(method_name))
    try:
        # Generate test input
        if method_name in ("values", "values_list"):
            res = method(f"{test_string}")
        elif method_name in ("filter", "exclude"):
            # print("Here is the filter shit: "+str(test_string))
            # print("Method: "+str(method))
            res = method(**{f"{test_string}": F("id")})
        elif method_name == "annotate":
            res = method(**{f"{test_string}": F("id")})
        elif method_name == "aggregate":
            # Just use the default aggregation of average
            # res = Author.objects.aggregate(**{crafted_alias: Avg("age")})
            res = method(**{test_string: Avg("id")}) # This is hardcoded for now...
        else:
            # try the explain stuff.
            qs = Model.objects.filter(name="test")

            # Try to craft malicious-looking options
            # The test_string will be the key of a kwarg passed to `.explain()`
            options = {test_string: True}

            # Evaluate the `.explain()` call with potentially dangerous options
            res = qs.explain(**options)

        # Evaluate the queryset to trigger potential DB errors
        list(res)  # force evaluation
    except Exception as e:
        # print("Exception caught:", type(e).__name__, str(e))
        raise  # or log it for crash deduplication

# Now let's implement this bullshit:

'''

def fuzz_queryset_explain(test_string):
    try:
        qs = Tag.objects.filter(name="test")

        # Try to craft malicious-looking options
        # The test_string will be the key of a kwarg passed to `.explain()`
        options = {test_string: True}

        # Evaluate the `.explain()` call with potentially dangerous options
        qs.explain(**options)
    except ValueError as e:
        print(f"Caught expected ValueError: {e}")
    except Exception as e:
        print(f"Caught unexpected {type(e).__name__}: {e}")

'''




# Test functions list

test_funcs = [target_queryset_alias, target_queryset_alias_json_field1, target_queryset_alias_json_field2, dynamic_fuzz_target, test_other_functions] # test_other_functions was added later on...

# Now here is the main fuzz function...

def fuzz_sqli(data: bytes): # Fuzz for SQL injection
    fh = open("input.bin", "wb")
    fh.write(data)
    fh.close()
    if len(data) < 2:
        return
    test_index = data[0] % len(test_funcs)
    assert isinstance(test_index, int)
    try:
        test_string = data.decode("utf-8") # Decode as utf-8
        # print("Here is the string: "+str(test_string))
        if "\x00" in test_string or "__range" in test_string: # "completed__range" in test_string: # Ban null bytes and another thing...
            return
    except:
        return # Just return if invalid utf-8
    # Now try to pass the thing
    func = test_funcs[test_index]
    try:
        func(test_string) # Call target function
    except (ValueError, FieldError, NotSupportedError): # Also catch NotSupportedError because there are lookups which aren't supported.
        # print("valueerror!!!")
        return
    except OperationalError as e:

        # user-defined function raised exception

        if "user-defined function raised exception" in str(e):
            return
        else:
            raise # Do not ignore other bullshit
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

def test3():
    '''
            elif method_name in ("filter", "exclude"):
            res = method(**{f"{test_string}": F("id")})
    '''
    # Company.objects.values(**{crafted_alias: F("ceo__salary")})
    # res = Experiment.objects.filter("completed__range")
    res = Experiment.objects.filter(**{"completed__range": F("id")}) # Maybe like this???
    list(res)
    return res


def create_model(start_datetime, end_datetime):
    return DTModel.objects.create(
        name=start_datetime.isoformat() if start_datetime else "None",
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        start_date=start_datetime.date() if start_datetime else None,
        end_date=end_datetime.date() if end_datetime else None,
        start_time=start_datetime.time() if start_datetime else None,
        end_time=end_datetime.time() if end_datetime else None,
        duration=(
            (end_datetime - start_datetime)
            if start_datetime and end_datetime
            else None
        ),
    )

def test4(): # Tests CVE-2022-34265 (https://github.com/django/django/commit/0dc9c016fadb71a067e5a42be30164e3f96c0492)
    start_datetime = datetime(2015, 6, 15, 14, 30, 50, 321)
    end_datetime = datetime(2016, 6, 15, 14, 10, 50, 123)
    if settings.USE_TZ:
        start_datetime = timezone.make_aware(start_datetime)
        end_datetime = timezone.make_aware(end_datetime)
    # self.create_model(start_datetime, end_datetime)
    # self.create_model(end_datetime, start_datetime)
    create_model(start_datetime, end_datetime)
    create_model(end_datetime, start_datetime)
    print("After creating the stuff...")
    msg = "Invalid lookup_name: "
    # with self.assertRaisesMessage(ValueError, msg):
    
    DTModel.objects.filter(
        start_datetime__year=Extract(
            "start_datetime", "day' FROM start_datetime)) OR 1=1;--"
        )
    ).exists()
    

    '''
    DTModel.objects.filter(
        start_datetime__year=Extract(
            "start_datetime", "day"
        )
    ).exists()
    '''
    print("[-] Did not raise exception!!!")

def test():
    # test0()
    # test1()
    test4()

if __name__=="__main__": # Only for testing.
    test()
    exit(0)
