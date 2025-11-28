
from django import forms
from django.conf import settings

# These are used for the sql fuzzing...

from django.db import models, connection
from django.db.utils import ProgrammingError, OperationalError
from django.db.models import Value, F # For the test stuff...
# For some exceptions...

from django.test.utils import CaptureQueriesContext

from django.core.exceptions import EmptyResultSet, FieldError, FullResultSet

import random

import django

import inspect # Needed for dynamic stuff

settings.configure(
    DEBUG=False, # Was originally "True,"
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

def test3():
    '''
            elif method_name in ("filter", "exclude"):
            res = method(**{f"{test_string}": F("id")})
    '''
    # Company.objects.values(**{crafted_alias: F("ceo__salary")})
    # res = Experiment.objects.filter("completed__range")
    # res = Experiment.objects.filter(**{"completed__range": F("id"), "name": "somestuffhere"}) # Maybe like this???
    # res = Experiment.objects.filter(**{"completed": F("id"), "name": "\"\" OR 1="}) # Maybe like this???
    malicious = "\"\" OR 1=1;--"
    res = Experiment.objects.filter(**{"name": malicious}) # Maybe like this???
    query_thing = res.query
    print("Here is the query: "+str(query_thing))
    list(res)
    return res






def test4():
    malicious = "\"\" OR 1=1;--"
    
    # Use CaptureQueriesContext to capture SQL queries
    with CaptureQueriesContext(connection) as queries:
        #try:
        # Execute the query with the malicious input
        # res = Experiment.objects.filter(name=malicious)
        # res = Experiment.objects.filter(**{"completed__range": F("id"), "name": "somestuffhere"})
        # res = Experiment.objects.filter(**{"completed__range": F("id"), "name": "somestuffhere"})
        # Force query execution (you need this for queries to actually be executed)
        list(res)
        #except OperationalError as e:
        #    print("Database error:", str(e))
        #    # return
        
    # Now, let's print the captured queries
    for query in queries:
        print(f"Captured SQL query: {query['sql']}")
        # print(f"Parameters: {query['params']}")





def test():
    # test3()
    test4()

if __name__=="__main__": # Only for testing.
    test()
    exit(0)
