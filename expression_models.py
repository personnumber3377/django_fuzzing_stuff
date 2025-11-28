# This file is ripped straight from https://github.com/django/django/blob/main/tests/expressions/models.py

import uuid

from django.db import models



class Manager(models.Model):
    name = models.CharField(max_length=50)
    secretary = models.ForeignKey(
        "Employee", models.CASCADE, null=True, related_name="managers"
    )
    class Meta:
        app_label = 'app'

class Employee(models.Model):
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    salary = models.IntegerField(blank=True, null=True)
    manager = models.ForeignKey(Manager, models.CASCADE, null=True)
    based_in_eu = models.BooleanField(default=False)

    def __str__(self):
        return "%s %s" % (self.firstname, self.lastname)
    class Meta:
        app_label = 'app'

class RemoteEmployee(Employee):
    adjusted_salary = models.IntegerField()
    class Meta:
        app_label = 'app'

class Company(models.Model):
    name = models.CharField(max_length=100)
    num_employees = models.PositiveIntegerField()
    num_chairs = models.PositiveIntegerField()
    ceo = models.ForeignKey(
        Employee,
        models.CASCADE,
        related_name="company_ceo_set",
    )
    point_of_contact = models.ForeignKey(
        Employee,
        models.SET_NULL,
        related_name="company_point_of_contact_set",
        null=True,
    )
    based_in_eu = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    class Meta:
        app_label = 'app'

class Number(models.Model):
    integer = models.BigIntegerField(db_column="the_integer")
    float = models.FloatField(null=True, db_column="the_float")
    decimal_value = models.DecimalField(max_digits=20, decimal_places=17, null=True)

    def __str__(self):
        return "%i, %.3f, %.17f" % (self.integer, self.float, self.decimal_value)
    class Meta:
        app_label = 'app'

class Experiment(models.Model):
    name = models.CharField(max_length=24)
    assigned = models.DateField()
    completed = models.DateField()
    estimated_time = models.DurationField()
    start = models.DateTimeField()
    end = models.DateTimeField()
    scalar = models.IntegerField(null=True)

    class Meta:
        db_table = "expressions_ExPeRiMeNt"
        ordering = ("name",)
        app_label = 'app'

    def duration(self):
        return self.end - self.start


class Result(models.Model):
    experiment = models.ForeignKey(Experiment, models.CASCADE)
    result_time = models.DateTimeField()

    def __str__(self):
        return "Result at %s" % self.result_time
    class Meta:
        app_label = 'app'

class Time(models.Model):
    time = models.TimeField(null=True)

    def __str__(self):
        return str(self.time)
    class Meta:
        app_label = 'app'

class SimulationRun(models.Model):
    start = models.ForeignKey(Time, models.CASCADE, null=True, related_name="+")
    end = models.ForeignKey(Time, models.CASCADE, null=True, related_name="+")
    midpoint = models.TimeField()

    def __str__(self):
        return "%s (%s to %s)" % (self.midpoint, self.start, self.end)
    class Meta:
        app_label = 'app'

class UUIDPK(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    class Meta:
        app_label = 'app'

class UUID(models.Model):
    uuid = models.UUIDField(null=True)
    uuid_fk = models.ForeignKey(UUIDPK, models.CASCADE, null=True)
    class Meta:
        app_label = 'app'

class JSONFieldModel(models.Model):
    data = models.JSONField(null=True)

    class Meta:
        required_db_features = {"supports_json_field"}
        app_label = 'app'





# This is from the aggregation stuff

class Author(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    friends = models.ManyToManyField("self", blank=True)
    rating = models.FloatField(null=True)

    def __str__(self):
        return self.name
    class Meta:
        app_label = 'app'

class Publisher(models.Model):
    name = models.CharField(max_length=255)
    num_awards = models.IntegerField()
    duration = models.DurationField(blank=True, null=True)

    def __str__(self):
        return self.name
    class Meta:
        app_label = 'app'

class Book(models.Model):
    isbn = models.CharField(max_length=9)
    name = models.CharField(max_length=255)
    pages = models.IntegerField()
    rating = models.FloatField()
    price = models.DecimalField(decimal_places=2, max_digits=6)
    authors = models.ManyToManyField(Author)
    contact = models.ForeignKey(Author, models.CASCADE, related_name="book_contact_set")
    publisher = models.ForeignKey(Publisher, models.CASCADE)
    pubdate = models.DateField()

    def __str__(self):
        return self.name
    class Meta:
        app_label = 'app'

class Store(models.Model):
    name = models.CharField(max_length=255)
    books = models.ManyToManyField(Book)
    original_opening = models.DateTimeField()
    friday_night_closing = models.TimeField()

    def __str__(self):
        return self.name
    class Meta:
        app_label = 'app'

class Employee_aggregation(models.Model):
    work_day_preferences = models.JSONField()
    class Meta:
        app_label = 'app'



# Taken from models.py in tests/db_functions/models.py

class DTModel(models.Model):
    name = models.CharField(max_length=32)
    start_datetime = models.DateTimeField(null=True, blank=True)
    end_datetime = models.DateTimeField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    class Meta:
        app_label = 'app'


# Taken from postgers_tests/models.py:


# Nevermind. Do not test postgresql

'''
class HStoreModel(PostgreSQLModel):
    field = HStoreField(blank=True, null=True)
    array_field = ArrayField(HStoreField(), null=True)
    class Meta:
        app_label = 'app'
'''

# These are needed for the tag and stuff...

class DumbCategory(models.Model):
    pass
    class Meta:
        app_label = 'app'

class ProxyCategory(DumbCategory):
    class Meta:
        proxy = True
        app_label = 'app'

class NamedCategory(DumbCategory):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name
    class Meta:
        app_label = 'app'


# Taken from tests/queries/models.py because reasons...

class Tag(models.Model):
    name = models.CharField(max_length=10)
    parent = models.ForeignKey(
        "self",
        models.SET_NULL,
        blank=True,
        null=True,
        related_name="children",
    )
    category = models.ForeignKey(
        NamedCategory, models.SET_NULL, null=True, default=None
    )

    class Meta:
        ordering = ["name"]
        app_label = 'app'

    def __str__(self):
        return self.name


class Note(models.Model):
    note = models.CharField(max_length=100)
    misc = models.CharField(max_length=25)
    tag = models.ForeignKey(Tag, models.SET_NULL, blank=True, null=True)
    negate = models.BooleanField(default=True)

    class Meta:
        ordering = ["note"]
        app_label = 'app'

    def __str__(self):
        return self.note



# This is for the thing...

class Experiment_thing(models.Model):
    start_datetime = models.DateTimeField()
    start_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_datetime = models.DateTimeField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    class Meta:
        app_label = 'app'


class FileFieldThing(models.Model):
    n = models.CharField(max_length=100)
    f = models.FileField(upload_to='')  # 'uploads/' is the directory inside MEDIA_ROOT


# Expression model names

expression_model_names = ["Manager",
    "Employee",
    "RemoteEmployee",
    "Company",
    "Number",
    "Experiment",
    "Result",
    "Time",
    "SimulationRun",
    "UUIDPK",
    "UUID",
    "JSONFieldModel",
    "Author",
    "Publisher",
    "Book",
    "Store",
    "Employee_aggregation",
    "DTModel",
    "Experiment_thing",
    "FileFieldThing"]
