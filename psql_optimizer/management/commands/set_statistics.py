
from django.db import connection, transaction
from django_tqdm import BaseCommand

from psql_optimizer.management.query.analyze_model import analyze_model
from psql_optimizer.management.query.set_stats import set_statistics


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--model')
        parser.add_argument('--column')
        parser.add_argument('--statistics')

    @transaction.atomic
    def handle(self, *args, **options):
        model = options.get('model')
        column = options.get('column')
        statistics = options.get('statistics')
        if model is None:
            self.stdout.write(
                self.style.ERROR(f"model is required"))
            self.stdout.write(
                self.style.ERROR(f"you can pass with --model"))
            return
        if column is None:
            self.stdout.write(
                self.style.ERROR(f"field is required"))
            self.stdout.write(
                self.style.ERROR(f"you can pass with --field"))
            return
        if statistics is None:
            self.stdout.write(
                self.style.ERROR(f"statistics length is required"))
            self.stdout.write(
                self.style.ERROR(f"you can pass with --statistics"))
            return

        with connection.cursor():
            self.stdout.write(
                self.style.SUCCESS(f"sending request to set statistics of "
                                   f"{column} on {model}"))
            set_statistics(model, column, statistics)
            self.stdout.write(
                self.style.SUCCESS("statistics is set"))
            should_analyze = input(
                f'do you want to analyze {model}? [y/N]: '
            ).lower().strip() == 'y'
            if should_analyze:
                self.stdout.write(
                    self.style.SUCCESS(f"analyzing {model} started"))
                analyze_model(model)
                self.stdout.write(
                    self.style.SUCCESS(f"finished analyzing {model}"))
