"""Experiment access module."""

import chamber.utilities.ddl as ddl
import mysql.connector


def build_experiment_tables(cursor):
    """
    Use cursor to build experiment tables.

    Parameters
    ----------
    cursor : mysql.connector.cursor.MySQLCursor
        mySQL cursor object

    Examples
    --------
    >>> build_experiment_tables(cursor)

    """
    for table in ddl.build_instructions['experiments', 'table order']:
        print('Creating table {}: '.format(table), end='')
        cursor.execute(
            ddl.build_instructions['experiments', 'ddl'][table]
            )
        print('OK')
