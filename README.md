# query-plan-optimizer
[![](https://img.shields.io/pypi/v/psql-stat-optimizer)](https://pypi.org/project/psql-stat-optimizer/) [![](https://img.shields.io/pypi/djversions/psql-stat-optimizer)](https://pypi.org/project/psql-stat-optimizer/)

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
- live_tup_count: the minimum number of n_live_tup to consider as a big table. *default is 100000*
- statistics: the statistics value you want to set to. *default is 10000*

### Using statistics command:

```bash
$ ./manage.py set_statistics
```

#### Parameters:
- model: the target model name
- column: the target column
- statistics: the target statistics

## TODO:
- remove time.sleep which is used for printing
- add command for analyze a table manually

