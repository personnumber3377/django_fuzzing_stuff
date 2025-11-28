
from django import forms
from django.conf import settings

# These are used for the sql fuzzing...

from django.db import models, connection
from django.db.utils import ProgrammingError
from django.db.models import Value, F # For the test stuff...
# from django.db.models import Value, F, Avg
# For some exceptions...

from django.core.exceptions import EmptyResultSet, FieldError, FullResultSet

import random

import django

import inspect # Needed for dynamic stuff

'''

Exception caught: FieldError Cannot resolve keyword 'taa_rt_da_tetimineMD' into field. Choices are: id, time
Here is the string: _Zcompleted__range
Model: Experiment
Method name: filter
Exception caught: OperationalError near "AND": syntax error
near "AND": syntax error
Exception encountered!!!!

 === Uncaught Python exception: ===
OperationalError: near "AND": syntax error
Traceback (most recent call last):
  File "/home/oof/djangosqlifuzz/django-fuzzers/fuzz_sqli.py", line 13, in TestOneInput
    fuzzers_sqli.fuzz_sqli(data)
  File "/home/oof/djangosqlifuzz/django-fuzzers/fuzzers_sqli.py", line 225, in fuzz_sqli
  File "/home/oof/djangosqlifuzz/django-fuzzers/fuzzers_sqli.py", line 194, in dynamic_fuzz_target
    return


 === Uncaught Python exception: ===
OperationalError: near "AND": syntax error
Traceback (most recent call last):
  File "/home/oof/djangosqlifuzz/django-fuzzers/fuzz_sqli.py", line 13, in TestOneInput
    fuzzers_sqli.fuzz_sqli(data)
  File "/home/oof/djangosqlifuzz/django-fuzzers/fuzzers_sqli.py", line 225, in fuzz_sqli
  File "/home/oof/djangosqlifuzz/django-fuzzers/fuzzers_sqli.py", line 194, in dynamic_fuzz_target
    return
  File "/home/oof/atheris-venv/lib/python3.11/site-packages/django/db/models/query.py", line 385, in __iter__
    self._fetch_all()
  File "/home/oof/atheris-venv/lib/python3.11/site-packages/django/db/models/query.py", line 1941, in _fetch_all
    self._result_cache = list(self._iterable_class(self))
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/oof/atheris-venv/lib/python3.11/site-packages/django/db/models/query.py", line 90, in __iter__
    results = compiler.execute_sql(
              ^^^^^^^^^^^^^^^^^^^^^
  File "/home/oof/atheris-venv/lib/python3.11/site-packages/django/db/models/sql/compiler.py", line 1623, in execute_sql
    cursor.execute(sql, params)
  File "/home/oof/atheris-venv/lib/python3.11/site-packages/django/db/backends/utils.py", line 79, in execute
    return self._execute_with_wrappers(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/oof/atheris-venv/lib/python3.11/site-packages/django/db/backends/utils.py", line 92, in _execute_with_wrappers
    return executor(sql, params, many, context)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/oof/atheris-venv/lib/python3.11/site-packages/django/db/backends/utils.py", line 100, in _execute
    with self.db.wrap_database_errors:
  File "/home/oof/atheris-venv/lib/python3.11/site-packages/django/db/utils.py", line 94, in __exit__
    raise dj_exc_value.with_traceback(traceback) from exc_value
  File "/home/oof/atheris-venv/lib/python3.11/site-packages/django/db/backends/utils.py", line 105, in _execute
    return self.cursor.execute(sql, params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/oof/atheris-venv/lib/python3.11/site-packages/django/db/backends/sqlite3/base.py", line 360, in execute
    return super().execute(query, params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
OperationalError: near "AND": syntax error

./fuzz_sqli.sh: line 2: 897505 Alarm clock             python3 fuzz_sqli.py -dict=dictionary_sqli.txt -max_len=100 -timeout=1 corp/
oof@elskun-lppri:~/djangosqlifuzz/django-fuzzers$ 

'''

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

def test3():
    '''
            elif method_name in ("filter", "exclude"):
            res = method(**{f"{test_string}": F("id")})
    '''
    # Company.objects.values(**{crafted_alias: F("ceo__salary")})
    # res = Experiment.objects.filter("completed__range")
    res = Experiment.objects.filter(**{"completed__range": F("id")}) # Maybe like this???
    query_thing = res.query
    print("Here is the query: "+str(query_thing))
    list(res)
    return res

def test():
    test3()

if __name__=="__main__": # Only for testing.
    test()
    exit(0)
