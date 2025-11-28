
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

def test2():
    # target_queryset_alias_json_field2("__ka___%PP")
    res = JSONFieldModel.objects.values_list("data__ka___%PP")
    list(res)
    return res

def test():
    test2()

if __name__=="__main__": # Only for testing.
    test()
    exit(0)
