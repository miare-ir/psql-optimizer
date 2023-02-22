from django.db import connection


def set_statistics(model, column):
    the_query = f'alter table {model} alter COLUMN {column} set statistics  10000'

    with connection.cursor() as cursor:
        cursor.execute(the_query)
