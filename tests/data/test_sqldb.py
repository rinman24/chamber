"""Docstring."""
import configparser
from datetime import datetime
from decimal import Decimal
from os import path
from pathlib import Path
from shutil import move

from math import isclose

import mysql.connector as conn
from mysql.connector.cursor import MySQLCursor
from mysql.connector import errorcode
import nptdms
import pytest

import chamber.const as const
from chamber.data import sqldb, _ddl, _dml
import tests.test_const as test_const

config = configparser.ConfigParser()
config.read('config.ini')

SETTINGS_TEST_1 = dict(Duty=10, Pressure=100000, Temperature=300)
SETTINGS_TEST_2 = dict(Duty=20, Pressure=110000, Temperature=270)

TDMS_01_THM_07 = '284.66'
TDMS_02_THM_07 = '283.55'
TDMS_03_THM_07 = '282.43'
TDMS_04_THM_07 = '282.29'

TEST_INDEX = 7
TC_INDEX = 7

TDMS_01_OBS_07 = dict(CapManOk=1, DewPoint='270.69', Idx=8, OptidewOk=1,
                      PowOut='-0.0003', PowRef='-0.0003', Pressure=100393,
                      Mass='0.0985090')
TDMS_02_OBS_07 = dict(CapManOk=1, DewPoint='270.93', Idx=7, OptidewOk=1,
                      PowOut='-0.0004', PowRef='-0.0001', Pressure=100428,
                      Mass='0.0985083')
TDMS_03_OBS_07 = dict(CapManOk=1, DewPoint='270.12', Idx=8, OptidewOk=1,
                      PowOut='-0.0002', PowRef='-0.0000', Pressure=100463)
TDMS_04_OBS_07 = dict(CapManOk=1, DewPoint='270.22', Idx=8, OptidewOk=1,
                      PowOut='-0.0003', PowRef='0.0001', Pressure=100520)

TDMS_01_TEST = dict(Author='author_01',
                    DateTime=datetime(2018, 1, 29, 17, 54, 12),
                    Description='description_01', IsMass=1, TimeStep=1)
TDMS_02_TEST = dict(Author='author_02',
                    DateTime=datetime(2018, 1, 29, 17, 55, 10),
                    Description='description_02', IsMass=1, TimeStep=1)
TDMS_03_TEST = dict(Author='author_03',
                    DateTime=datetime(2018, 1, 29, 17, 50, 58),
                    Description='description_03', IsMass=0, TimeStep=1)
TDMS_04_TEST = dict(Author='author_04',
                    DateTime=datetime(2018, 1, 29, 17, 52, 24),
                    Description='description_04', IsMass=0, TimeStep=1)


@pytest.fixture(scope='module')
def cursor():
    """Cursor Fixture at module level so that only one connection is made."""
    print("\nConnecting to MySQL...")
    cnx, cur = sqldb.connect("test")
    print("Connected.")
    yield cur
    print("\nCleaning up test database...")
    drop_tables(cur, True)
    print("Disconnecting from MySQL...")
    cnx.commit()
    cur.close()
    cnx.close()
    print("Connection to MySQL closed.")


@pytest.fixture(scope='module')
def test_tdms_obj():
    """Fixture to instantiate only one nptdms.TdmsFile object for testing."""
    return (  # IsMass 1 Duty 5%
            nptdms.TdmsFile(test_const.CORRECT_FILE_LIST[0]),
            # IsMass 1 Duty 0%
            nptdms.TdmsFile(test_const.CORRECT_FILE_LIST[1]),
            # IsMass 0 Duty 5%
            nptdms.TdmsFile(test_const.CORRECT_FILE_LIST[2]),
            # IsMass 0 Duty 0%
            nptdms.TdmsFile(test_const.CORRECT_FILE_LIST[3]))


def test_connect(cursor):
        """Test connection to database."""
        assert cursor
        assert isinstance(cursor, MySQLCursor)


def test_create_tables(cursor):
    """Test creation of tables."""
    # Create the tables
    assert sqldb.create_tables(cursor, _ddl.tables)

    # Now check that all tables exist
    table_names_set = set(_ddl.table_name_list)
    cursor.execute("SHOW TABLES;")
    for row in cursor:
        assert row[0] in table_names_set


def test_setting_exists(cursor):
    """Test setting_exists."""
    cursor.execute(_dml.add_setting, SETTINGS_TEST_1)
    assert sqldb.setting_exists(cursor, SETTINGS_TEST_1)
    assert not sqldb.setting_exists(cursor, SETTINGS_TEST_2)
    truncate(cursor, 'Setting')


def test_get_temp_info(test_tdms_obj):
    """Test get_temp_info."""
    assert (
        TDMS_01_THM_07 ==
        sqldb.get_temp_info(test_tdms_obj[0], TEST_INDEX, TC_INDEX)
        )
    assert (
        TDMS_02_THM_07 ==
        sqldb.get_temp_info(test_tdms_obj[1], TEST_INDEX, TC_INDEX)
        )
    assert (
        TDMS_03_THM_07 ==
        sqldb.get_temp_info(test_tdms_obj[2], TEST_INDEX, TC_INDEX)
        )
    assert (
        TDMS_04_THM_07 ==
        sqldb.get_temp_info(test_tdms_obj[3], TEST_INDEX, TC_INDEX)
        )


def test_get_setting_info(test_tdms_obj):
        """Test get_setting_info."""
        assert (
            test_const.TDMS_01_SETTING ==
            sqldb.get_setting_info(test_tdms_obj[0])
            )
        assert (
            test_const.TDMS_02_SETTING ==
            sqldb.get_setting_info(test_tdms_obj[1])
            )
        assert (
            test_const.TDMS_03_SETTING ==
            sqldb.get_setting_info(test_tdms_obj[2])
            )
        assert (
            test_const.TDMS_02_SETTING ==
            sqldb.get_setting_info(test_tdms_obj[3])
            )  # This is the same setting at 2


def test_get_test_info(test_tdms_obj):
        """Test get_test_info."""
        assert TDMS_01_TEST == sqldb.get_test_info(test_tdms_obj[0])
        assert TDMS_02_TEST == sqldb.get_test_info(test_tdms_obj[1])
        assert TDMS_03_TEST == sqldb.get_test_info(test_tdms_obj[2])
        assert TDMS_04_TEST == sqldb.get_test_info(test_tdms_obj[3])


def test_get_obs_info(test_tdms_obj):
        """Test get_obs_info."""
        assert (
            TDMS_01_OBS_07 ==
            sqldb.get_obs_info(test_tdms_obj[0], TEST_INDEX)
            )
        assert (
            TDMS_02_OBS_07 ==
            sqldb.get_obs_info(test_tdms_obj[1], TEST_INDEX)
            )
        assert (
            TDMS_03_OBS_07 ==
            sqldb.get_obs_info(test_tdms_obj[2], TEST_INDEX)
            )
        assert (
            TDMS_04_OBS_07 ==
            sqldb.get_obs_info(test_tdms_obj[3], TEST_INDEX)
            )


def test_add_tube_info(cursor):
    """Test add_tube_info."""
    assert sqldb.add_tube_info(cursor)
    cursor.execute("SELECT TubeID FROM Tube;")
    assert cursor.fetchone()[0] == 1
    cursor.execute("SELECT TubeID FROM Tube;")
    assert len(cursor.fetchall()) == 1

    cursor.execute("SELECT DiameterIn FROM Tube WHERE TubeID=1;")
    assert cursor.fetchone()[0] == Decimal('0.0300000')

    cursor.execute("SELECT DiameterOut FROM Tube WHERE TubeID=1;")
    assert cursor.fetchone()[0] == Decimal('0.0400000')

    cursor.execute("SELECT Length FROM Tube WHERE TubeID=1;")
    assert cursor.fetchone()[0] == Decimal('0.0600000')

    cursor.execute("SELECT Material FROM Tube WHERE TubeID=1;")
    assert cursor.fetchone()[0] == 'Delrin'

    cursor.execute("SELECT Mass FROM Tube WHERE TubeID=1;")
    assert cursor.fetchone()[0] == Decimal('0.0873832')

    assert not sqldb.add_tube_info(cursor)


class TestSqlDb(object):
    """Unit testing of sqldb.py."""

    def test_add_setting_info(self, cursor, test_tdms_obj):
        """Test data insertion and condition handling in add_setting."""
        sqldb.add_setting_info(cursor, test_tdms_obj[0])
        setting_id = sqldb.setting_exists(cursor, sqldb.get_setting_info(
                                                    test_tdms_obj[0]))
        assert setting_id == 1

        sqldb.add_setting_info(cursor, test_tdms_obj[1])
        setting_id = sqldb.setting_exists(cursor, sqldb.get_setting_info(
                                                    test_tdms_obj[1]))
        assert setting_id == 2

        sqldb.add_setting_info(cursor, test_tdms_obj[2])
        setting_id = sqldb.setting_exists(cursor, sqldb.get_setting_info(
                                                    test_tdms_obj[2]))
        assert setting_id == 3

        sqldb.add_setting_info(cursor, test_tdms_obj[3])
        setting_id = sqldb.setting_exists(cursor, sqldb.get_setting_info(
                                                    test_tdms_obj[3]))
        assert setting_id == 2  # This test has the same setting at 2

    def test_add_test_info(self, cursor, test_tdms_obj):
        """Test correct data insertion and condition handling in add_test."""
        sqldb.add_test_info(cursor, test_tdms_obj[0], 1)
        cursor.execute('SELECT * FROM Test WHERE TestID={}'.format(
                       cursor.lastrowid))
        assert cursor.fetchall() == test_const.TDMS_01_ADD_TEST

        sqldb.add_test_info(cursor, test_tdms_obj[1], 2)
        cursor.execute('SELECT * FROM Test WHERE TestID={}'.format(
                       cursor.lastrowid))
        assert cursor.fetchall() == test_const.TDMS_02_ADD_TEST

        sqldb.add_test_info(cursor, test_tdms_obj[2], 3)
        cursor.execute('SELECT * FROM Test WHERE TestID={}'.format(
                       cursor.lastrowid))
        assert cursor.fetchall() == test_const.TDMS_03_ADD_TEST

        sqldb.add_test_info(cursor, test_tdms_obj[3], 2)
        cursor.execute('SELECT * FROM Test WHERE TestID={}'.format(
                       cursor.lastrowid))
        assert cursor.fetchall() == test_const.TDMS_04_ADD_TEST

    def test_test_exists(self, cursor, test_tdms_obj):
        """Test that you can find tests that already exist."""
        assert 1 == sqldb.test_exists(cursor, TDMS_01_TEST)
        assert 2 == sqldb.test_exists(cursor, TDMS_02_TEST)
        assert 3 == sqldb.test_exists(cursor, TDMS_03_TEST)
        assert 4 == sqldb.test_exists(cursor, TDMS_04_TEST)
        assert not 5 == sqldb.test_exists(cursor, TDMS_01_TEST)
        assert not 6 == sqldb.test_exists(cursor, '')

    def test_add_obs_info(self, cursor, test_tdms_obj):
        """Test correct data insertion and condition handling in add_obs."""
        for tdms_idx in range(
                len(test_tdms_obj[0].object("Data", "Idx").data)
                ):
            sqldb.add_obs_info(cursor, test_tdms_obj[0], 1, tdms_idx)
        cursor.execute(test_const.GET_LAST_DEW_POINT.format(1))
        assert cursor.fetchall()[0][0] == Decimal('270.78')

        for tdms_idx in range(
                len(test_tdms_obj[1].object("Data", "Idx").data)
                ):
            sqldb.add_obs_info(cursor, test_tdms_obj[1], 2, tdms_idx)
        cursor.execute(test_const.GET_LAST_DEW_POINT.format(2))
        assert cursor.fetchall()[0][0] == Decimal('270.93')

        for tdms_idx in range(
                len(test_tdms_obj[2].object("Data", "Idx").data)
                ):
            sqldb.add_obs_info(cursor, test_tdms_obj[2], 3, tdms_idx)
        cursor.execute(test_const.GET_LAST_DEW_POINT.format(3))
        assert cursor.fetchall()[0][0] == Decimal('270.20')

        for tdms_idx in range(
                len(test_tdms_obj[3].object("Data", "Idx").data)
                ):
            sqldb.add_obs_info(cursor, test_tdms_obj[3], 4, tdms_idx)
        cursor.execute(test_const.GET_LAST_DEW_POINT.format(4))
        assert cursor.fetchall()[0][0] == Decimal('270.32')

    def test_add_temp(self, cursor, test_tdms_obj):
        """Test temperature insert and condition handling in add_temp."""
        sqldb.add_temp_info(cursor, test_tdms_obj[0], 1, TEST_INDEX,
                            TEST_INDEX+1)
        cursor.execute(
            test_const.GET_TEMP_OBS.format(1, TEST_INDEX+1)
            )
        res = [float(r[0]) for r in cursor.fetchall()]
        assert res == test_const.TEMP_OBS_1

        sqldb.add_temp_info(cursor, test_tdms_obj[1], 2,
                            TEST_INDEX, TEST_INDEX)
        cursor.execute(
            test_const.GET_TEMP_OBS.format(2, TEST_INDEX)
            )
        res = [float(r[0]) for r in cursor.fetchall()]
        assert res == test_const.TEMP_OBS_2

        sqldb.add_temp_info(cursor, test_tdms_obj[2], 3,
                            TEST_INDEX, TEST_INDEX+1)
        cursor.execute(
            test_const.GET_TEMP_OBS.format(3, TEST_INDEX+1)
            )
        res = [float(r[0]) for r in cursor.fetchall()]
        assert res == test_const.TEMP_OBS_3

        sqldb.add_temp_info(cursor, test_tdms_obj[3], 4,
                            TEST_INDEX, TEST_INDEX+1)
        cursor.execute(
            test_const.GET_TEMP_OBS.format(4, TEST_INDEX+1)
            )
        res = [float(r[0]) for r in cursor.fetchall()]
        assert res == test_const.TEMP_OBS_4

    def test_add_data(self, cursor):
        """Test overall data insertion, the final table in cascade."""
        truncate(cursor, 'Observation')
        truncate(cursor, 'Test')
        truncate(cursor, 'Setting')

        fp = path.join(test_const.TEST_DIRECTORY, 'test_01.tdms')
        sqldb.add_data(cursor, fp, True)
        cursor.execute(
            test_const.GET_OBS_DATA_M.format(1, TEST_INDEX)
            )
        res = cursor.fetchall()[0]
        for i in range(len(res)):
            assert isclose(res[i], test_const.OBS_DATA_1[i])

        fp = path.join(test_const.TEST_DIRECTORY, 'tdms_test_folder',
                       'test_02.tdms')
        sqldb.add_data(cursor, fp, True)
        cursor.execute(
            test_const.GET_OBS_DATA_M.format(2, TEST_INDEX)
            )
        res = cursor.fetchall()[0]
        for i in range(len(res)):
            assert isclose(res[i], test_const.OBS_DATA_2[i])

        fp = path.join(test_const.TEST_DIRECTORY, 'test_03.tdms')
        sqldb.add_data(cursor, fp, True)
        cursor.execute(
            test_const.GET_OBS_DATA_T.format(3, TEST_INDEX)
            )
        res = cursor.fetchall()[0]
        for i in range(len(res)):
            assert isclose(res[i], test_const.OBS_DATA_3[i])

        fp = path.join(test_const.TEST_DIRECTORY, 'tdms_test_folder',
                       'tdms_test_folder_full', 'test_04.tdms')
        sqldb.add_data(cursor, fp, True)
        cursor.execute(
            test_const.GET_OBS_DATA_T.format(4, TEST_INDEX)
            )
        res = cursor.fetchall()[0]
        for i in range(len(res)):
            assert isclose(res[i], test_const.OBS_DATA_4[i])


def drop_tables(cursor, bol):
    """Drop databese tables if bol is true."""
    if bol:
        print("Dropping tables...")
        cursor.execute("DROP TABLE IF EXISTS " +
                       ", ".join(_ddl.table_name_list) + ";")
    else:
        print("Tables not dropped.")


def truncate(cursor, table):
    """Truncate tables."""
    cursor.execute('SET FOREIGN_KEY_CHECKS=0')
    cursor.execute('TRUNCATE {}'.format(table))
    cursor.execute('SET FOREIGN_KEY_CHECKS=1')


# def test_list_tdms(self):
    #     """Can tdms files be located?"""
    #     files = sqldb.list_tdms(test_const.TEST_DIRECTORY)
    #     assert len(files) == len(test_const.CORRECT_FILE_LIST)
    #     for f in files:
    #         assert f not in test_const.INCORRECT_FILE_LIST
    #         assert f in test_const.CORRECT_FILE_LIST

    # def test_move_files(self):
    #     """Test that files are removed from the directory and into user."""
    #     try:
    #         assert path.exists(test_const.CORRECT_FILE_LIST[2])
    #         sqldb.move_files(path.split(test_const.CORRECT_FILE_LIST[2])[0])
    #         assert not path.exists(test_const.CORRECT_FILE_LIST[2])
    #         new_path = path.join(
    #             path.join(str(Path.home()), "read_files"),
    #             path.relpath(test_const.CORRECT_FILE_LIST[2])[3:])
    #         assert path.exists(new_path)
    #         move(new_path, path.split(test_const.CORRECT_FILE_LIST[2])[0])
    #     except FileNotFoundError:
    #         assert False
