import time

from django.apps import apps
from django.db import connection, transaction
from django_tqdm import BaseCommand

from psql_optimizer.management.query.analyze_model import analyze_model
from psql_optimizer.management.query.find_table import find_tables
from psql_optimizer.management.query.set_stats import set_statistics


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--set_all')
        parser.add_argument('--analyze_all')
        parser.add_argument('--live_tup_count')

    @transaction.atomic
    def handle(self, *args, **options):
        set_all = options.get('set_all', False)
        analyze_all = options.get('analyze_all', False)
        live_tup_count = options.get('live_tup_count', 100000)
        with connection.cursor() as cursor:
            cursor.execute(find_tables(live_tup_count))
            result = self.retrieve_models_from_result(cursor)
            result_count = len(result)
            self.stdout.write(self.style.SUCCESS(f"found {result_count} models to set statistics"))
            self.stdout.write(
                self.style.SUCCESS(f"founded models:"))
            self.print_founded_models(result)

            if set_all:
                should_set = True
            else:
                should_set = input(
                    'set statistics for founded models? [y/N]: ').lower().strip() == 'y'

            if should_set:
                self.stdout.write(
                    self.style.NOTICE("start setting statistics..."))
                t = self.tqdm(total=result_count)
                for model in result:
                    self.add_statistics(model, analyze_all, t)
                    t.update(1)

    @staticmethod
    def retrieve_models_from_result(cursor):
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def add_statistics(self, model_dict, analyze_all, t):
        db_model = model_dict['relname']
        live_tuples_count = model_dict['n_live_tup']
        try:
            model_name, app_label = self.find_model_name(db_model)
        except:
            time.sleep(0.05)
            return
        self.stdout.write(self.style.SUCCESS(f"set statistics for related models to {db_model}"))
        t.info(f"\tnumber of live tuples: {live_tuples_count}")

        try:
            model = apps.get_model(app_label=app_label, model_name=model_name)
        except:
            t.error(f"\t{db_model} is not valid model to set statistics for")
            return

        related_model_objects = model._meta.get_fields()

        self.set_statistics(related_model_objects, analyze_all, t)
        time.sleep(0.05)
        return

    def print_founded_models(self, models):
        for r in models:
            model_name = r['relname']
            self.stdout.write(
                self.style.SUCCESS(f"\t{model_name}"))

    @staticmethod
    def find_model_name(db_model):
        model_name = db_model.split('_')[-1]
        total_count = len(db_model.split('_')) - 1
        app_labeled = db_model.split('_')[0:total_count]
        if len(app_labeled) == 1:
            app_label = app_labeled[0]
        else:
            app_label = '_'.join(app_labeled)

        return model_name, app_label

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
                set_statistics(db_converted_model, r_column)
                t.info("\tstatistics is set")

                analyze_query = f'analyze verbose {db_converted_model}'

                if analyze_all:
                    should_analyze = True
                else:
                    should_analyze = input(
                        f'do you want to analyze {db_converted_model}? [y/N]: '
                    ).lower().strip() == 'y'
                if should_analyze:
                    t.info(f"\tstart analyzing {db_converted_model}")
                    analyze_model(analyze_query)
                    t.info(f"\tfinished analyzing {db_converted_model}")
            except AttributeError:
                continue
