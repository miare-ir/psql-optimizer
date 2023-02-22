

def find_tables():
    find_big_tables = """
    select relname, n_live_tup from pg_stat_user_tables where n_live_tup > 100000 and seq_scan > 1000
    """

    return find_big_tables
