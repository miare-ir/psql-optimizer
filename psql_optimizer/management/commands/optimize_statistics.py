import time

from django.apps import apps
from django.db import connection, transaction
from django_tqdm import BaseCommand

from psql_optimizer.management.commands.func import find_model_name
from psql_optimizer.management.query.analyze_model import analyze_model
from psql_optimizer.management.query.find_table import find_tables
from psql_optimizer.management.query.set_stats import set_statistics


class Command(BaseCommand):
    STATISTICS = None
    LIVE_TUPLES_COUNT = None

    def add_arguments(self, parser):
        parser.add_argument('--set_all')
        parser.add_argument('--analyze_all')
        parser.add_argument('--live_tup_count')
        parser.add_argument('--statistics')

    @transaction.atomic
    def handle(self, *args, **options):
        set_all = options.get('set_all', False)
        analyze_all = options.get('analyze_all', False)
        self.LIVE_TUPLES_COUNT = options.get('live_tup_count') or 100000
        self.STATISTICS = options.get('statistics') or 10000

        with connection.cursor() as cursor:
            cursor.execute(find_tables(self.LIVE_TUPLES_COUNT))
            result = self.retrieve_models_from_result(cursor)
            result_count = len(result)
            self.stdout.write(self.style.SUCCESS(f"found {result_count} models to set statistics"))
            self.stdout.write(
                self.style.SUCCESS(f"founded models:"))
            self.print_founded_models(result)

            t = self.tqdm(total=result_count)
            if set_all:
                self.stdout.write(
                    self.style.NOTICE("start setting statistics..."))
                for model in result:
                    self.add_statistics(model, analyze_all, t)
                    t.update(1)
            else:
                for model in result:
                    should_set = input(
                        f'do you want to set statistics for {model}? [y/N]: ').lower(

                    ).strip() == 'y'
                    t.update(1)
                    if should_set:
                        self.add_statistics(model, analyze_all, t)

    @staticmethod
    def retrieve_models_from_result(cursor):
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def add_statistics(self, model_dict, analyze_all, t):
        table = model_dict['relname']
        live_tuples_count = model_dict['n_live_tup']
        try:
            model_name, app_label = find_model_name(table)
            model = apps.get_model(app_label=app_label, model_name=model_name)
        except:
            t.error(f"\t{table} is not valid table to set statistics for")
            time.sleep(0.05)
            return
        self.stdout.write(self.style.SUCCESS(f"set statistics for related tables to {table}"))
        t.info(f"\tnumber of live tuples: {live_tuples_count}")

        related_model_objects = model._meta.get_fields()

        self.set_statistics(related_model_objects, analyze_all, t)
        time.sleep(0.05)
        return

    def print_founded_models(self, models):
        for r in models:
            model_name = r['relname']
            l_tup_count = r['n_live_tup']
            self.stdout.write(
                self.style.SUCCESS(f"\t{model_name}, live_tuples_count: {l_tup_count}"))

    def set_statistics(self, related_model_objects, analyze_all, t):
        for obj in related_model_objects:
            try:
                r_model = obj.related_model
                r_column = obj.field.attname

                r_model_count = r_model.objects.all().count()
                if r_model_count < 20000:
                    t.info(f"\trecords of {r_model} model are not enough to set statistics")
                    continue
                app_label = r_model._meta.app_label
                r_model_name = r_model._meta.model_name
                db_converted_model = f"{app_label}_{r_model_name}"

                t.info(
                    f"\tsending request to set statistics of {r_column} on {db_converted_model}")
                error = set_statistics(db_converted_model, r_column, self.STATISTICS)
                if error:
                    t.error("\tstatistics is not set, due to an error")
                    continue
                t.info("\tstatistics is set")

                if analyze_all:
                    should_analyze = True
                else:
                    should_analyze = input(
                        f'do you want to analyze {db_converted_model}? [y/N]: '
                    ).lower().strip() == 'y'
                if should_analyze:
                    t.info(f"\tstart analyzing {db_converted_model}")
                    error = analyze_model(db_converted_model)
                    if error:
                        t.error(f"\tanalyzing {db_converted_model} did not finish successfully")
                        continue
                    t.info(f"\tfinished analyzing {db_converted_model}")
            except AttributeError:
                continue
