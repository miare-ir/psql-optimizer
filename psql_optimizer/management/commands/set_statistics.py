from django.apps import apps
from django.db import transaction
from django_tqdm import BaseCommand

from psql_optimizer.management.commands.func import find_model_name
from psql_optimizer.management.query.analyze_model import analyze_model
from psql_optimizer.management.query.set_stats import set_statistics


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--table')
        parser.add_argument('--column')
        parser.add_argument('--statistics')

    @transaction.atomic
    def handle(self, *args, **options):
        table = options.get('table')
        column = options.get('column')
        statistics = options.get('statistics')
        self._validate_table(table)
        self._validate_column(column)
        if statistics is None:
            self.stdout.write(
                self.style.INFO(f"statistics is not set. Default value of 10000 will be "
                                f"considered"))
            statistics = 10000

        self._set_statistics(table, column, statistics)

    def _validate_table(self, table):
        if table is None:
            self.stdout.write(
                self.style.ERROR("table is required"))
            self.stdout.write(
                self.style.ERROR("you can pass with --table"))
            return

        try:
            model_name, app_label = find_model_name(table)
            apps.get_model(app_label=app_label, model_name=model_name)
        except:
            self.stdout.write(
                self.style.ERROR(f"\t{table} is not valid model to set statistics for"))

    def _validate_column(self, column):
        if column is None:
            self.stdout.write(
                self.style.ERROR(f"field is required"))
            self.stdout.write(
                self.style.ERROR(f"you can pass with --field"))
            return

    def _set_statistics(self, table, column, statistics):
        self.stdout.write(
            self.style.SUCCESS(f"sending request to set statistics of "
                               f"{column} on {table}"))
        error = set_statistics(table, column, statistics)
        if error:
            self.stdout.write(
                self.style.ERROR("an error happened while setting statistics"))
            self.stdout.write(
                self.style.ERROR("check table name and column and retry again"))
            return
        self.stdout.write(
            self.style.SUCCESS("statistics is set"))
        self._validate_table(table)

    def _analyze_table(self, table):
        should_analyze = input(
            f'do you want to analyze {table}? [y/N]: '
        ).lower().strip() == 'y'
        if should_analyze:
            self.stdout.write(
                self.style.SUCCESS(f"analyzing {table} started"))
            err = analyze_model(table)
            if err:
                self.stdout.write(
                    self.style.ERROR(f"an error happened while analyzing {table}"))
                return
            self.stdout.write(
                self.style.SUCCESS(f"finished analyzing {table}"))
