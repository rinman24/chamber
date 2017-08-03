"""Docstring."""
from math import isclose
import mysql.connector as conn
from mysql.connector import errorcode
import pytest

import chamber.sqldb as sqldb

TABLES = []
TABLES.append(('UnitTest',
               "CREATE TABLE `UnitTest` ("
               "    `UnitTestID` TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,"
               "    `Value` DECIMAL(5,2) NOT NULL,"
               "    `String` VARCHAR(30) NOT NULL,"
               "  PRIMARY KEY (`UnitTestID`)"
               ");"))

SETTINGS_1 = {'InitialDewPoint': '100', 'InitialDuty': '100', 'InitialMass': '0.07',
              'InitialPressure': '100000', 'InitialTemp': '290', 'TimeStep': '1'}
SETTINGS_2 = {'InitialDewPoint': '500', 'InitialDuty': '1000', 'InitialMass': '20',
              'InitialPressure': '8', 'InitialTemp': '400', 'TimeStep': '20'}

@pytest.fixture(scope='module')
def cursor():
    """Cursor Fixture at module level so that only one connection is made."""
    print("\nConnecting to MySQL...")
    cnx = sqldb.connect_sqldb()
    cur = cnx.cursor()
    print("Connected.")
    yield cur
    print("\nCleaning up test database...")
    cur.execute("DROP TABLE UnitTest;")
    print("Disconnecting from MySQL...")
    cnx.commit()
    cur.close()
    cnx.close()
    print("Connection to MySQL closed.")

class TestSqlDb(object):
    """Unit testing of sqldb.py."""

    def test_connection(self, cursor):
        """Test connection to the MySQL database."""
        assert cursor

    def test_create_table(self, cursor):
        """"Test DDL for table creation."""
        sqldb.create_tables(cursor, TABLES)
        cursor.execute("SELECT 1 FROM UnitTest LIMIT 1;")
        assert len(cursor.fetchall()) == 0

    def test_enter_into_table(self, cursor):
        """Test DDL for row insertion."""        
        add_row = ("INSERT INTO UnitTest (Value, String) VALUES (%s, %s);")
        row_data = ('99.9', 'Test String')
        sqldb.table_insert(cursor, add_row, row_data)
        cursor.execute("SELECT Value FROM UnitTest WHERE String = 'Test String';")
        assert isclose(float(cursor.fetchall()[0][0]), 99.9)

    def test_setting_exists(self, cursor):
        """Test that you can find settings that already exist."""
        add_row = ("INSERT INTO Setting"
                   "(InitialDewPoint, InitialDuty, InitialMass,"
                   " InitialPressure, InitialTemp, TimeStep)"
                   "  VALUES (%s, %s, %s, %s, %s, %s);")
        row_data = ('100', '100.0', '0.07', '100000', '290.0', '1.0')
        sqldb.table_insert(cursor, add_row, row_data)
        assert sqldb.setting_exists(cursor, SETTINGS_1)
        assert not sqldb.setting_exists(cursor, SETTINGS_2)
        cursor.execute("DELETE FROM Setting WHERE InitialDewPoint = 100;")
