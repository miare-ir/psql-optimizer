
from django.db import transaction
from django_tqdm import BaseCommand

from psql_optimizer.management.query.analyze_model import analyze_model
from psql_optimizer.management.query.set_stats import set_statistics


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--table')
        parser.add_argument('--column')
        parser.add_argument('--statistics')

    @transaction.atomic
    def handle(self, *args, **options):
        model = options.get('table')
        column = options.get('column')
        statistics = options.get('statistics') or 10000
        if model is None:
            self.stdout.write(
                self.style.ERROR(f"table is required"))
            self.stdout.write(
                self.style.ERROR(f"you can pass with --table"))
            return
        if column is None:
            self.stdout.write(
                self.style.ERROR(f"field is required"))
            self.stdout.write(
                self.style.ERROR(f"you can pass with --field"))
            return
        if statistics is None:
            self.stdout.write(
                self.style.INFO(f"statistics is not set. Default value of 10000 will be "
                                f"considered"))

        self.stdout.write(
            self.style.SUCCESS(f"sending request to set statistics of "
                               f"{column} on {model}"))
        error = set_statistics(model, column, statistics)
        if error:
            self.stdout.write(
                self.style.ERROR("an error happened while setting statistics"))
            self.stdout.write(
                self.style.ERROR("check table name and column and retry again"))
            return
        self.stdout.write(
            self.style.SUCCESS("statistics is set"))
        should_analyze = input(
            f'do you want to analyze {model}? [y/N]: '
        ).lower().strip() == 'y'
        if should_analyze:
            self.stdout.write(
                self.style.SUCCESS(f"analyzing {model} started"))
            err = analyze_model(model)
            if err:
                self.stdout.write(
                    self.style.ERROR(f"an error happened while analyzing {model}"))
                return
            self.stdout.write(
                self.style.SUCCESS(f"finished analyzing {model}"))
