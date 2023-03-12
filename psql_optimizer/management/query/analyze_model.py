from django.db import connection


def analyze_model(model) -> bool:
    the_query = f'analyze verbose {model}'
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET LOCAL statement_timeout to \'10 min \';')
            cursor.execute(the_query)
            return False
    except:
        return True
