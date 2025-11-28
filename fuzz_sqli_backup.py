import sys

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
        print(e)
        print("Exception encountered!!!!")
        raise
    return


atheris.Setup(sys.argv, TestOneInput)
atheris.Fuzz()
