"""Docstring. This module sets up the initial state of the database. Be sure to only run onece."""

# The first thing I need to do is get a connection to the database.
# This will provide a connection as cnx and a cursor as cur.
import chamber.sqldb as sqldb
print("Loaded chamber.sqldb modulesucessfully.")

# Now that I have the module loaded, I can use it to make a connection.
cnx = sqldb.connect_sqldb()
print("Sucessfully created a connection to the database")

cur = cnx.cursor()
print("Sucessfully created a cursor for the database")

# Now that I have a connection to the database, I need to create several tables.
# I can use the create_tables method from chamber.sqldb.
# I just need to make several dictionaries that hold the info, see below:

TABLES = {}
TABLES['Unit'] = (
    "CREATE TABLE Unit ("
    "    Duty VARCHAR(30) NOT NULL,"
    "    Length VARCHAR(30) NOT NULL,"
    "    Mass VARCHAR(30) NOT NULL,"
    "    Power VARCHAR(30) NOT NULL,"
    "    Pressure VARCHAR(30) NOT NULL,"
    "    Temperature VARCHAR(30) NOT NULL,"
    "    Time VARCHAR(30) NOT NULL"
    ");")
TABLES['Tube'] = (
    "CREATE TABLE Tube("
    "    TubeID TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,"
    "    DiameterIn DECIMAL(7, 7) NOT NULL,"
    "    DiameterOut DECIMAL(7, 7) NOT NULL,"
    "    Length DECIMAL(4, 4) NOT NULL,"
    "    Material VARCHAR(30) NOT NULL,"
    "    Mass DECIMAL(7, 7) NOT NULL,"
    "  PRIMARY KEY (TubeID)"
    ");")
TABLES['Setting'] = (
    "CREATE TABLE Setting("
    "    SettingID SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,"
    "    InitialDewPoint DECIMAL(5, 2) NOT NULL,"
    "    InitialDuty DECIMAL(4, 1) NOT NULL,"
    "    InitialMass DECIMAL(7, 7) NOT NULL,"
    "    InitialPressure MEDIUMINT UNSIGNED NOT NULL,"
    "    InitialTemp DECIMAL(5, 2) NOT NULL,"
    "    TimeStep DECIMAL(4, 2) NOT NULL,"
    "  PRIMARY KEY (SettingID)"
    ");")
TABLES['Test'] = (
    "CREATE TABLE Test("
    "    TestID SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,"
    "    DateTime DATETIME NOT NULL,"
    "    IsCal TINYINT(1) NOT NULL,"
    "    SettingID SMALLINT UNSIGNED NOT NULL,"
    "    TubeID TINYINT UNSIGNED NOT NULL,"
    "  PRIMARY KEY (TestID),"
    "  FOREIGN KEY (SettingID) REFERENCES Setting(SettingID)"
    "    ON UPDATE CASCADE ON DELETE RESTRICT,"
    "  FOREIGN KEY (TubeID) REFERENCES Tube(TubeID)"
    "    ON UPDATE CASCADE ON DELETE RESTRICT"
    ");")
TABLES['Observation'] = (
    "CREATE TABLE Observation("
    "    ObservationID SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,"
    "    DewPoint DECIMAL(5, 2) NOT NULL,"
    "    Idx SMALLINT UNSIGNED NOT NULL,"
    "    Mass DECIMAL(7, 7) NOT NULL,"
    "    PowOut DECIMAL(6, 4) NOT NULL,"
    "    PowRef DECIMAL(6, 4) NOT NULL,"
    "    Pressure MEDIUMINT UNSIGNED NOT NULL,"
    "    TestID SMALLINT UNSIGNED NOT NULL,"
    "  PRIMARY KEY (ObservationID),"
    "  FOREIGN KEY (TestID) REFERENCES Test(TestID)"
    "    ON UPDATE CASCADE ON DELETE RESTRICT"
    ");")
TABLES['TempObservation'] = (
    "CREATE TABLE TempObservation("
    "    TempObservationID INT UNSIGNED NOT NULL AUTO_INCREMENT,"
    "    Location VARCHAR(30) NULL DEFAULT NULL,"
    "    Temperature DECIMAL(5, 2) NOT NULL,"
    "    ThermocoupleNum TINYINT(2) UNSIGNED NOT NULL,"
    "    ObservationID SMALLINT UNSIGNED NOT NULL,"
    "  PRIMARY KEY (TempObservationID),"
    "  FOREIGN KEY (ObservationID) REFERENCES Observation(ObservationID)"
    "    ON UPDATE CASCADE ON DELETE RESTRICT"
    ");")

print("Starting to create tables...")
sqldb.create_tables(cur, TABLES)

print("Populating Units table...")
ADD_ROW_UNIT = (
	"INSERT INTO Unit"
	"    (Duty, Length, Mass, Power, Pressure, Temperature, Time) "
	"  VALUES "
	"    (%s, %s, %s, %s, %s, %s, %s)"
	";")
ROW_DATA_UNIT = ('Percent', 'Meter', 'Kilogram', 'Watt', 'Pascal', 'Kelvin', 'Second')
sqldb.table_insert(cur, ADD_ROW_UNIT, ROW_DATA_UNIT)

print("Committing changes to Unit table...")
cnx.commit()

print("All done, closing connection to server...")
cnx.close()
print("Closed the connection.")
