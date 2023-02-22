# query-plan-optimizer

Postgresql Statistics are vital for a good query plan. This library finds tables with large number of live tuples and tries to find related models with foreign key to the model and sets statistics for the field on destination model.

## Installation
```bash
$ pip install psql-stat-optimizer
```
add `psql_optimizer` to your `INSTALLED_APPS`

## usage:
### Using full optimize command:

```bash
$ ./manage.py optimize_statistics
```

#### Valid Parameters:
- set_all: if passed as `True` it sets for all founded models automatically
- analyze_all: if passed as `True` it analyzes all models after their statistics is changed

## TODO:
- remove time.sleep which is used for printing
- add command for set statistics manually
- add command for analyze a table manually

