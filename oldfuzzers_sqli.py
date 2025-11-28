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
from django.db.models import Value, F, Avg, Sum, Count, Min, Max, StdDev # For the test stuff...

func_stuff = [Avg, Sum, Count, Min, Max, StdDev]

# For some exceptions...

from django.core.exceptions import EmptyResultSet, FieldError, FullResultSet# , NotSupportedError # Not in exceptions, because reasons.

from django.db.utils import NotSupportedError, OperationalError

# These next things is for the other thing

from django.http.response import JsonResponse
# from datetime import datetime


from django.db.models.functions import Concat, Coalesce, Extract, Trunc, JSONObject, Lower
from django.db.models import DateTimeField, CharField # from django.db.models import Value, CharField
# from vuln.models import Experiment
from django.core import serializers

from django.utils import timezone # For some stuff

# django.db.utils.OperationalError

# from django.db.utils.OperationalError

import random

import django

from json import JSONDecodeError

import inspect # Needed for dynamic stuff

ARGUMENT_SEPARATOR_STRING = "A" # This is to cut the input fuzz string and stuff.

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
    DEBUG=False, # Was originally "True,"
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


def setup_experiment_bullshit():
    #

    sday = sday = datetime.date(2010, 6, 25)
    stime = stime = datetime.datetime(2010, 6, 25, 12, 15, 30, 747000)
    midnight = datetime.time(0)

    delta0 = datetime.timedelta(0)
    delta1 = datetime.timedelta(microseconds=253000)
    delta2 = datetime.timedelta(seconds=44)
    delta3 = datetime.timedelta(hours=21, minutes=8)
    delta4 = datetime.timedelta(days=10)
    delta5 = datetime.timedelta(days=90)

    # Test data is set so that deltas and delays will be
    # strictly increasing.
    deltas = []
    delays = []
    days_long = []

    # e0: started same day as assigned, zero duration
    end = stime + delta0
    e0 = Experiment.objects.create(
        name="e0",
        assigned=sday,
        start=stime,
        end=end,
        completed=end.date(),
        estimated_time=delta0,
    )
    deltas.append(delta0)
    delays.append(
        e0.start - datetime.datetime.combine(e0.assigned, midnight)
    )
    days_long.append(e0.completed - e0.assigned)

    # e1: started one day after assigned, tiny duration, data
    # set so that end time has no fractional seconds, which
    # tests an edge case on sqlite.
    delay = datetime.timedelta(1)
    end = stime + delay + delta1
    e1 = Experiment.objects.create(
        name="e1",
        assigned=sday,
        start=stime + delay,
        end=end,
        completed=end.date(),
        estimated_time=delta1,
    )
    deltas.append(delta1)
    delays.append(e1.start - datetime.datetime.combine(e1.assigned, midnight))
    days_long.append(e1.completed - e1.assigned)

    # e2: started three days after assigned, small duration
    end = stime + delta2
    e2 = Experiment.objects.create(
        name="e2",
        assigned=sday - datetime.timedelta(3),
        start=stime,
        end=end,
        completed=end.date(),
        estimated_time=datetime.timedelta(hours=1),
    )
    deltas.append(delta2)
    delays.append(e2.start - datetime.datetime.combine(e2.assigned, midnight))
    days_long.append(e2.completed - e2.assigned)

    # e3: started four days after assigned, medium duration
    delay = datetime.timedelta(4)
    end = stime + delay + delta3
    e3 = Experiment.objects.create(
        name="e3",
        assigned=sday,
        start=stime + delay,
        end=end,
        completed=end.date(),
        estimated_time=delta3,
    )
    deltas.append(delta3)
    delays.append(e3.start - datetime.datetime.combine(e3.assigned, midnight))
    days_long.append(e3.completed - e3.assigned)

    # e4: started 10 days after assignment, long duration
    end = stime + delta4
    e4 = Experiment.objects.create(
        name="e4",
        assigned=sday - datetime.timedelta(10),
        start=stime,
        end=end,
        completed=end.date(),
        estimated_time=delta4 - datetime.timedelta(1),
    )
    deltas.append(delta4)
    delays.append(e4.start - datetime.datetime.combine(e4.assigned, midnight))
    days_long.append(e4.completed - e4.assigned)

    # e5: started a month after assignment, very long duration
    delay = datetime.timedelta(30)
    end = stime + delay + delta5
    e5 = Experiment.objects.create(
        name="e5",
        assigned=sday,
        start=stime + delay,
        end=end,
        completed=end.date(),
        estimated_time=delta5,
    )
    deltas.append(delta5)
    delays.append(e5.start - datetime.datetime.combine(e5.assigned, midnight))
    days_long.append(e5.completed - e5.assigned)

    expnames = [e.name for e in Experiment.objects.all()]

    return

from decimal import Decimal

def setup_more_stuff():
    d = datetime.timedelta(days =-1, seconds = 68400)
    # Now setup the shit here.
    example = DurationFieldModel.objects.create(dt=d)



    example_inc = Company.objects.create(
        name="Example Inc.",
        num_employees=2300,
        num_chairs=5,
        ceo=Employee.objects.create(firstname="Joe", lastname="Smith", salary=10),
    )
    foobar_ltd = Company.objects.create(
        name="Foobar Ltd.",
        num_employees=3,
        num_chairs=4,
        based_in_eu=True,
        ceo=Employee.objects.create(firstname="Frank", lastname="Meyer", salary=20),
    )
    max = Employee.objects.create(
        firstname="Max", lastname="Mustermann", salary=30
    )
    gmbh = Company.objects.create(
        name="Test GmbH", num_employees=32, num_chairs=1, ceo=max
    )


    ceo = Employee.objects.create(firstname="Just", lastname="Doit", salary=30)
    # MySQL requires that the values calculated for expressions don't pass
    # outside of the field's range, so it's inconvenient to use the values
    # in the more general tests.
    c5020 = Company.objects.create(
        name="5020 Ltd", num_employees=50, num_chairs=20, ceo=ceo
    )
    c5040 = Company.objects.create(
        name="5040 Ltd", num_employees=50, num_chairs=40, ceo=ceo
    )
    c5050 = Company.objects.create(
        name="5050 Ltd", num_employees=50, num_chairs=50, ceo=ceo
    )
    c5060 = Company.objects.create(
        name="5060 Ltd", num_employees=50, num_chairs=60, ceo=ceo
    )
    c99300 = Company.objects.create(
        name="99300 Ltd", num_employees=99, num_chairs=300, ceo=ceo
    )

    setup_experiment_bullshit()






    a1 = Author.objects.create(name="Adrian Holovaty", age=34)
    a2 = Author.objects.create(name="Jacob Kaplan-Moss", age=35)
    a3 = Author.objects.create(name="James Bennett", age=34)
    a4 = Author.objects.create(name="Peter Norvig", age=57)
    a5 = Author.objects.create(name="Stuart Russell", age=46)
    p1 = Publisher.objects.create(name="Apress", num_awards=3)

    b1 = Book.objects.create(
        isbn="159059725",
        pages=447,
        rating=4.5,
        price=Decimal("30.00"),
        contact=a1,
        publisher=p1,
        pubdate=datetime.date(2007, 12, 6),
        name="The Definitive Guide to Django: Web Development Done Right",
    )
    b2 = Book.objects.create(
        isbn="159059996",
        pages=300,
        rating=4.0,
        price=Decimal("29.69"),
        contact=a3,
        publisher=p1,
        pubdate=datetime.date(2008, 6, 23),
        name="Practical Django Projects",
    )
    b3 = Book.objects.create(
        isbn="013790395",
        pages=1132,
        rating=4.0,
        price=Decimal("82.80"),
        contact=a4,
        publisher=p1,
        pubdate=datetime.date(1995, 1, 15),
        name="Artificial Intelligence: A Modern Approach",
    )
    b4 = Book.objects.create(
        isbn="155860191",
        pages=946,
        rating=5.0,
        price=Decimal("75.00"),
        contact=a4,
        publisher=p1,
        pubdate=datetime.date(1991, 10, 15),
        name=(
            "Paradigms of Artificial Intelligence Programming: Case Studies in "
            "Common Lisp"
        ),
    )
    b1.authors.add(a1, a2)
    b2.authors.add(a3)
    b3.authors.add(a4, a5)
    b4.authors.add(a4)

    Store.objects.create(
        name="Amazon.com",
        original_opening=datetime.datetime(1994, 4, 23, 9, 17, 42),
        friday_night_closing=datetime.time(23, 59, 59),
    )
    Store.objects.create(
        name="Books.com",
        original_opening=datetime.datetime(2001, 3, 15, 11, 23, 37),
        friday_night_closing=datetime.time(23, 59, 59),
    )











    return

def setup_stuff(): # This creates the shit..
    

    setup_more_stuff()
    from datetime import datetime # Now we maybe put this here????
    start_datetime = datetime(2015, 6, 15, 14, 30, 50, 321)
    end_datetime = datetime(2016, 6, 15, 14, 10, 50, 123)
    if settings.USE_TZ:
        start_datetime = timezone.make_aware(start_datetime)
        end_datetime = timezone.make_aware(end_datetime)
    # self.create_model(start_datetime, end_datetime)
    # self.create_model(end_datetime, start_datetime)
    create_model(start_datetime, end_datetime)
    create_model(end_datetime, start_datetime)

    Author.objects.bulk_create(
            [
                Author(name="Ivan Ivanov", alias="iivanov"),
                Author(name="Bertha Berthy", alias="bberthy"),
            ]
        )

    # 

    return

setup_stuff()



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
interesting_methods_no_explain = ["filter", "values", "values_list", "annotate", "aggregate", "exclude"]
# These functions are taken from 

# Fuzzing function for testing JSONObject
def vuln_json_object(test_string):
    try:
        payload = test_string
        # Dynamically create the JSON object with fuzzed test string
        res = Author.objects.annotate(
            json_object=JSONObject(
                name=Lower("name"),
                alias=payload,
                goes_by="goes_by",
                salary=Value(30000.15),
                age=F(payload) * 2,
                extra_field=payload  # Inject fuzzed value here
            )
        ).first()
        return res.json_object
    except Exception as e:
        raise
        # return str(e)  # Return error message to capture unexpected behavior
    return

def vuln_extract(test_string):
    payload = test_string
    res = DTModel.objects.filter(start_datetime__year=Extract('end_datetime', str(payload))).exists() # Originally also had '''"day' FROM
    return res # JsonResponse({"res": serializers.serialize("json", experiments)})

# /trunc/?kind=xxx
def vuln_trunc(test_string):
    # print("Here is the test_string: "+str(test_string))
    payload = test_string
    res = DTModel.objects.filter(start_datetime__date=Trunc('start_datetime', str(payload))).exists()
    return res


# These are the other functions similar to Extract and Trunc:

def pick_model(test_string):
    model_name = expression_model_names[ord(test_string[0]) % len(expression_model_names)]
    # method_name = interesting_methods_no_explain[ord(test_string[1]) % len(interesting_methods_no_explain)]
    test_string = test_string[1:] # Cut the thing...
    
    # Get the model class from app registry
    # Model = apps.get_model('app', model_name)
    # print("Model: "+str(model_name))
    assert model_name in globals()
    Model = globals()[model_name]

    return Model, test_string

# 1. F() Expressions
def vuln_f_expression(test_string):
    payload = test_string
    if len(test_string) <= 2:
        return None
    model, payload = pick_model(payload)
    # Example fuzz: Use an F expression to compare fields with a dynamic payload
    res = model.objects.filter(start_datetime__year=F(payload)).exists()
    return res

# 2. Coalesce()
def vuln_coalesce(test_string):
    payload = test_string
    if len(test_string) <= 2:
        return None
    model, payload = pick_model(payload)
    # Example fuzz: Coalesce with a dynamic payload
    res = model.objects.filter(start_datetime__year=Coalesce(F(payload), 0)).exists()
    return res

# 3. Concat()
def vuln_concat(test_string):
    payload = test_string
    if len(test_string) <= 2:
        return None
    model, payload = pick_model(payload)
    # Example fuzz: Concatenate with a dynamic payload
    # Cut the thing here...
    if ARGUMENT_SEPARATOR_STRING in payload:
        things = payload.split(ARGUMENT_SEPARATOR_STRING)
        first_thing = things.pop(0)
        other_thing = ''.join(things) # Just join the rest together...
    else:
        first_thing = 'name'
        other_thing = payload
    res = model.objects.annotate(
        concatenated_value=Concat(F(first_thing), Value(other_thing), output_field=CharField())
    ).exists()
    # print("poopooo"*1000)
    return res

from django.db.models.fields.json import HasKey
from django.db.models import JSONField

def json_contains_shit(test_string):
    # def target_queryset_alias_json_field2(test_string):
    # res = JSONFieldModel.objects.values_list(f"data__{test_string}")
    # list(res)
    # JSONFieldModel.objects.values_list(f"data__{test_string}")
    # res = SomeModel.objects.filter(meta_data__icontains=test_string).exists()
    res = JSONFieldModel.objects.filter(data__description__icontains=test_string).exists()
    # list(res)
    # print("pooopoo"*1000)
    return

'''

    def test_has_key_literal_lookup(self):
        self.assertSequenceEqual(
            NullableJSONModel.objects.filter(
                HasKey(Value({"foo": "bar"}, JSONField()), "foo")
            ).order_by("id"),
            self.objs,
        )

'''

def json_has_key(test_string):
    res = JSONFieldModel.objects.filter(HasKey(Value({test_string: "bar"}, JSONField()), test_string)).order_by("id")
    list(res)
    # print("fuckfuck"*1000)
    return res


vuln_stuff = [vuln_extract, vuln_trunc, vuln_f_expression, vuln_coalesce, vuln_concat, vuln_json_object, json_contains_shit, json_has_key] # These are the function stuff shit...

def test_other_functions(test_string):
    if len(test_string) <= 1:
        return
    vuln_func_thing = vuln_stuff[ord(test_string[0]) % len(vuln_stuff)]
    test_string = test_string[1:]
    # Now call the thing...
    vuln_func_thing(test_string) # Call that shit.
    return

def get_two_string(string):
    thing = string.split(ARGUMENT_SEPARATOR_STRING)
    return thing[0], thing[1]

def dynamic_explain_target(test_string): # This is basically only for the thing...
    # print("poopoo")
    # Random model and ORM method
    if len(test_string) <= 2:
        return
    model_name = expression_model_names[ord(test_string[0]) % len(expression_model_names)]
    method_name = interesting_methods_no_explain[ord(test_string[1]) % len(interesting_methods_no_explain)]
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
            if ARGUMENT_SEPARATOR_STRING in test_string:
                a,b = get_two_string(test_string)
                res = method(**{f"{a}": F(b)})
            else:
                res = method(**{f"{test_string}": F("id")})
        elif method_name == "annotate":
            # res = method(**{f"{test_string}": F("id")})
            if ARGUMENT_SEPARATOR_STRING in test_string:
                a,b = get_two_string(test_string)
                res = method(**{f"{a}": F(b)})
            else:
                res = method(**{f"{test_string}": F("id")})
        elif method_name == "aggregate":
            # Just use the default aggregation of average
            # res = Author.objects.aggregate(**{crafted_alias: Avg("age")})
            # res = method(**{test_string: Avg("id")}) # This is hardcoded for now...
            if ARGUMENT_SEPARATOR_STRING in test_string:
                # print("Fuck!!!!"*1000)
                a,b = get_two_string(test_string)
                # func_stuff
                if a != "":
                    the_function = func_stuff[ord(a[0]) % len(func_stuff)] # Now do the shit...
                else:
                    the_function = func_stuff[0] # Just pick the first one...
                # print("Now doing the thing...")
                # print("a: "+str(a))
                # print("the_function: "+str(the_function))
                # print("b: "+str(b))
                res = method(**{a: the_function(b)})
                # print("Fuck22222!!!!"*1000)
            else:
                res = method(**{test_string: Avg("id")})

        # Evaluate the queryset to trigger potential DB error
    except Exception as e:
        # print("Exception caught:", type(e).__name__, str(e))
        raise  # or log it for crash deduplication
    # try the explain stuff.
    list(res)
    qs = res # Model.objects.filter(name="test")

    # Try to craft malicious-looking options
    # The test_string will be the key of a kwarg passed to `.explain()`
    options = {test_string: True, "analyze": True}

    # Evaluate the `.explain()` call with potentially dangerous options
    # print("Dynamic explain bullshit before!!!")
    # print(res)
    if isinstance(res, dict):
        return
    # print("Dynamic explain bullshit!!!")
    res = qs.explain(**options)
    list(res)
    
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
        '''
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
        '''
        #print("Method name: "+str(method_name))
        if method_name in ("values", "values_list"):
            res = method(f"{test_string}")
        elif method_name in ("filter", "exclude"):
            # print("Here is the filter shit: "+str(test_string))
            # print("Method: "+str(method))
            if ARGUMENT_SEPARATOR_STRING in test_string:
                a,b = get_two_string(test_string)
                #print("model_name: "+str(model_name))
                #print("poopoooo:::")
                #print("a: "+str(a))
                #print("b: "+str(b))
                res = method(**{f"{a}": F(b)})
            else:
                res = method(**{f"{test_string}": F("id")})
        elif method_name == "annotate":
            # res = method(**{f"{test_string}": F("id")})
            if ARGUMENT_SEPARATOR_STRING in test_string:
                a,b = get_two_string(test_string)
                res = method(**{f"{a}": F(b)})
            else:
                res = method(**{f"{test_string}": F("id")})
        elif method_name == "aggregate":
            # Just use the default aggregation of average
            # res = Author.objects.aggregate(**{crafted_alias: Avg("age")})
            # res = method(**{test_string: Avg("id")}) # This is hardcoded for now...
            if ARGUMENT_SEPARATOR_STRING in test_string:
                a,b = get_two_string(test_string)
                res = method(**{a: Avg(b)})
            else:
                res = method(**{test_string: Avg("id")})

        else:
            # try the explain stuff.
            '''
            qs = Model.objects.filter(name="test")

            # Try to craft malicious-looking options
            # The test_string will be the key of a kwarg passed to `.explain()`
            options = {test_string: True}

            # Evaluate the `.explain()` call with potentially dangerous options
            res = qs.explain(**options)
            '''
            dynamic_explain_target(test_string)
            return
        # Evaluate the queryset to trigger potential DB errors
        list(res)  # force evaluation
    except Exception as e:
        # print("Exception caught:", type(e).__name__, str(e))
        raise  # or log it for crash deduplication

# Now let's implement this bullshit:




# Test functions list

test_funcs = [target_queryset_alias, target_queryset_alias_json_field1, target_queryset_alias_json_field2, dynamic_fuzz_target, test_other_functions] # test_other_functions was added later on...

# Now here is the main fuzz function...

def fuzz_sqli(data: bytes): # Fuzz for SQL injection
    # fh = open("input.bin", "wb")
    # fh.write(data)
    # fh.close()
    if len(data) < 2:
        return
    test_index = data[0] % len(test_funcs)
    assert isinstance(test_index, int)
    try:
        test_string = data.decode("utf-8") # Decode as utf-8
        # print("Here is the string: "+str(test_string))
        if "\x00" in test_string: #  or "__range" in test_string: # "completed__range" in test_string: # Ban null bytes and another thing...
            return
    except:
        return # Just return if invalid utf-8
    # Now try to pass the thing
    func = test_funcs[test_index]
    try:
        func(test_string) # Call target function
    except (FieldError, NotSupportedError, RecursionError) as e: # (ValueError, FieldError, NotSupportedError) as e: # Also catch NotSupportedError because there are lookups which aren't supported.
        # print("valueerror!!!")
        # print(e)
        return
    except JSONDecodeError as e:
        return

    except ValueError as e:
        # ValueError: Column aliases cannot contain whitespace characters, quotation marks, semicolons, or SQL comments.
        # Cutout all of the known exceptions...
        if "Column aliases cannot contain whitespace" not in str(e) and "conflicts with a field on " not in str(e) and "Invalid option name" not in str(e) and "Unknown options" not in str(e) and "must be True or False" not in str(e):
            raise
    except OperationalError as e:
        # print(e)
        # user-defined function raised exception

        if "user-defined function raised exception" in str(e) or "user-defined aggregate" in str(e) or "range" in test_string: # Ignore exceptions in user defined functions...
            # print("User defined bullshit exception!!!"*10000)
            return
        else:
            print("shitfuck"*10000)
            fh = open("exploit.bin", "wb")
            fh.write(data)
            fh.close()
            raise # Do not ignore other bullshit
    except TypeError as e: # TypeError: not enough arguments for format string
        # print(e)
        if "not enough arguments for format string" in str(e) or "object does not support item assignment" in str(e): # This bug here is not exploitable so just patch that shit out for now...
            return
        else:
            raise
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
    '''
    start_datetime = datetime(2015, 6, 15, 14, 30, 50, 321)
    end_datetime = datetime(2016, 6, 15, 14, 10, 50, 123)
    if settings.USE_TZ:
        start_datetime = timezone.make_aware(start_datetime)
        end_datetime = timezone.make_aware(end_datetime)
    # self.create_model(start_datetime, end_datetime)
    # self.create_model(end_datetime, start_datetime)
    create_model(start_datetime, end_datetime)
    create_model(end_datetime, start_datetime)
    '''
    setup_stuff() # Setup the shit..
    print("After creating the stuff...")
    msg = "Invalid lookup_name: "
    # with self.assertRaisesMessage(ValueError, msg):
    
    DTModel.objects.filter(
        start_datetime__year=Extract(
            "start_datetime", "day' FROM start_datetime)) OR 1=1;--"
        )
    ).exists()
    print("[-] Did not raise exception!!!")
    return

def test():
    # test0()
    # test1()
    test4()

import sys

if __name__=="__main__": # Only for testing.
    # test()
    if len(sys.argv) != 2:
        print("Please pass in input filename!!!!")
        exit(1)
    fh = open(sys.argv[1], "rb")
    data_stuff = fh.read()
    fh.close()
    fuzz_sqli(data_stuff)
    exit(0)
