from django.db import connection


def set_statistics(model, column, statistics):
    the_query = f'alter table {model} alter COLUMN {column} set statistics {statistics}'

    try:
        with connection.cursor() as cursor:
            cursor.execute(the_query)
    except:
        return
