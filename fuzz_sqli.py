import sys

import mutator

import atheris

with atheris.instrument_imports():
    import fuzzers_sqli


def TestOneInput(data):
    assert isinstance(data, bytes)
    try:
        # func(data)
        fuzzers_sqli.fuzz_sqli(data)
    except Exception as e:
        # print(func, data_type, repr(data))
        #print(e)
        #print("Exception encountered!!!!")
        raise
    return

def CustomMutator(data, max_size, seed):
    try:
        res = mutator.mutate(data) # Call custom mutator.
    except:
        res = atheris.Mutate(data, len(data))
    else:
        res = atheris.Mutate(res, len(res))
    if len(res) >= max_size: # Truncate inputs which are too long...
        return res[:max_size]
    return res

# atheris.Setup(sys.argv, TestOneInput, custom_mutator=CustomMutator, internal_libfuzzer=True) # Use the custom mutator

atheris.Setup(sys.argv, TestOneInput)
atheris.Fuzz()
