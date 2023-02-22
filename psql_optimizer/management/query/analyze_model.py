from django.db import connection


def analyze_model(model):
    the_query = f'analyze verbose {model}'
    with connection.cursor() as cursor:
        cursor.execute(the_query)
