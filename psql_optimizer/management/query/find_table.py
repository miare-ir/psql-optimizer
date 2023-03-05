

def find_tables(n_live_tup_count):
    find_big_tables = """
    select relname, n_live_tup from pg_stat_user_tables where n_live_tup > {n_live_tup}
    """.format(n_live_tup=n_live_tup_count)

    return find_big_tables
