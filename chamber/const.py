"""Constants for the UCSD Chamber Experiment."""

from datetime import datetime
from decimal import Decimal
from math import log, sqrt
from os import getcwd

import pytz

# ZnSe port parameters (From Spec Sheet)
D_PORT = 2.286e-2 # 2.286 cm         [X]
R_PORT = 1.143e-2 # 1.143 cm         [X]
A_PORT = 4.104e-4 # 4.104 cm^2       [X]

# Beam Parameters
"""
The cross-sectional area of the beam is chosen to be half of the area of the ZnSe aperature. As a
result, the radius of the beam will be smaller by a factor of 1/sqrt(2).
LAM  : wavelength of radiation
W_0  : beam radius at laser head
POW  : total power transmitted by the beam
Z_0  : Rayleigh length at the laser head
W_COL: beam radius after collimation
D_B  : diamter of the beam after collimation
A_CB : cross-sectional area of the beam after collimation
"""
LAM = 10.59e-6 # 10.59 microns          [X]
W_0 = 0.9e-3 # 0.9 mm                   [X]
POW = 20 # 20 W                         [X]
Z_0 = 24.03e-2 # 24.03 cm               [X]
W_COL = 8.082e-3 # 8.082 mm             [X]
D_B = 1.616e-2 # 1.616 cm               [X]
A_CB = 2.052e-4 # 2.052 cm^2            [X]

# Stefan Tube Dimensions
D_IN_TUBE = 2.286e-2 # 2.286 cm         [X]
R_IN_TUBE = 1.143e-2 # 1.143 cm         [X]
A_C_TUBE = 4.104e-4 # 4.104 cm^2        [X]
D_OUT_TUBE = 3.4e-2 # 3.4 cm            [X]
R_OUT_TUBE = 1.7e-2 # 1.7 cm            [X]
H_IN_TUBE = 4.572e-2 # 4.572 cm         [X]
H_OUT_TUBE = 5.129e-2 # 5.129 cm        [X]
H_TUBE_BASE = 5.57e-3 # 5.57 mm         [X]

# Gaussian Beam Constants
HWHM_COEFF_W = sqrt(2*log(2))/2 # 0.589 [X]

# Liquid Water Optical Properties at 10.59 microns
K_ABS_10P6 = 8.218e4 # 82,180 m^{-1}    []
K_EXT_10P6 = 6.925e-2 # 0.06925         []
L_K_ABS = 1.22e-5 # 12 microns          []

# Liquid Water Thermal Properties
# (273.15 to 373.15 K)
K_L_COEFF = [-2.9064388, 2.692925e-2, -6.8256489e-05, 5.858084e-08]
C_L_COEFF = [1.1844879e+06, -2.1559968e+04, 1.6404218e+02, -6.6524994e-01, 1.5161227e-03,
             -1.8406899e-06, 9.2992482e-10]
RHO_L_COEFF = [-7.2156278e+04, 1.1366432e+03, -7.0513426e+00, 2.1835039e-02, -3.3746407e-05,
               2.0814924e-08]


#Hardy Equation Constants
G_COEF = (-2.8365744e3, -6.028076559e3, 1.954263612e1, -2.737830188e-2, 1.6261698e-5,
          7.0229056e-10, -1.8680009e-13, 2.7150305)

A_COEF = (-1.6302041e-1, 1.8071570e-3, -6.7703064e-6, 8.5813609e-9)

B_COEF = (-5.9890467e1, 3.4378043e-1, -7.7326396e-4, 6.3405286e-7)

# MySQL Constants
FIND_SETTING = ("SELECT SettingID FROM Setting WHERE "
                "    InitialDewPoint = %(InitialDewPoint)s AND"
                "    InitialDuty = %(InitialDuty)s AND"
                "    InitialMass = %(InitialMass)s AND"
                "    InitialPressure = %(InitialPressure)s AND"
                "    InitialTemp = %(InitialTemp)s AND"
                "    TimeStep = %(TimeStep)s;")

FIND_TUBE = ("SELECT TubeID FROM Tube WHERE "
             "    DiameterIn = %(DiameterIn)s AND"
             "    DiameterOut = %(DiameterOut)s AND"
             "    Length = %(Length)s AND"
             "    Material = %(Material)s AND"
             "    Mass = %(Mass)s")

FIND_TEST = ("SELECT TestID FROM Test WHERE "
             "    DateTime = %(DateTime)s")

FIND_TESTID = ("SELECT TestID FROM Test WHERE "
             "    TestID = (%s)")

ADD_SETTING = ("INSERT INTO Setting "
               "(InitialDewPoint, InitialDuty, InitialMass, InitialPressure, InitialTemp, TimeStep)"
               " VALUES "
               "(%(InitialDewPoint)s, %(InitialDuty)s, %(InitialMass)s, %(InitialPressure)s, "
               "%(InitialTemp)s, %(TimeStep)s)")

ADD_TEST = ("INSERT INTO Test "
            "(Author, DateTime, Description, SettingID, TubeID)"
            " VALUES "
            "(%(Author)s, %(DateTime)s, %(Description)s, %(SettingID)s, %(TubeID)s)")

ADD_OBS = ("INSERT INTO Observation "
           "(CapManOk, DewPoint, Duty, Idx, Mass, OptidewOk, PowOut, PowRef, Pressure, TestID)"
           " VALUES "
           "(%(CapManOk)s, %(DewPoint)s, %(Duty)s, %(Idx)s, %(Mass)s, %(OptidewOk)s, %(PowOut)s,"
           " %(PowRef)s, %(Pressure)s, %(TestID)s)")

ADD_TEMP = ("INSERT INTO TempObservation "
            "(ObservationID, ThermocoupleNum, Temperature)"
            " VALUES "
            "(%s, %s, %s)")

ADD_TUBE = ("INSERT INTO Tube "
            "(DiameterIn, DiameterOut, Length, Material, Mass)"
            " VALUES "
            "(%(DiameterIn)s, %(DiameterOut)s, %(Length)s, %(Material)s, %(Mass)s)")

ADD_UNIT = ("INSERT INTO Unit "
            "(Duty, Length, Mass, Power, Pressure, Temperature, Time)"
            " VALUES "
            "(%(Duty)s, %(Length)s, %(Mass)s, %(Power)s, %(Pressure)s, %(Temperature)s, %(Time)s)")

TUBE_DATA = {'DiameterIn': 0.03, 'DiameterOut': 0.04, 'Length': 0.06,
             'Material': 'Delrin', 'Mass': 0.0657957}

UNIT_DATA = {'Duty': 'Percent', 'Length': 'Meter', 'Mass': 'Kilogram', 'Power': 'Watt',
             'Pressure': 'Pascal', 'Temperature': 'Kelvin', 'Time': 'Second'}

# MySQL Test Constants
TABLES = []
TABLES.append(('UnitTest',
           "CREATE TABLE UnitTest ("
           "    UnitTestID TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,"
           "    Number DECIMAL(5,2) NULL,"
           "    String VARCHAR(30) NULL,"
           "  PRIMARY KEY (`UnitTestID`)"
           ");"))
TABLES.append(('Unit',
               "CREATE TABLE Unit ("
               "    Duty VARCHAR(30) NOT NULL,"
               "    Length VARCHAR(30) NOT NULL,"
               "    Mass VARCHAR(30) NOT NULL,"
               "    Power VARCHAR(30) NOT NULL,"
               "    Pressure VARCHAR(30) NOT NULL,"
               "    Temperature VARCHAR(30) NOT NULL,"
               "    Time VARCHAR(30) NOT NULL"
               ");"))
TABLES.append(('Tube',
               "CREATE TABLE Tube("
               "    TubeID TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,"
               "    DiameterIn DECIMAL(7, 7) NOT NULL,"
               "    DiameterOut DECIMAL(7, 7) NOT NULL,"
               "    Length DECIMAL(4, 4) NOT NULL,"
               "    Material VARCHAR(30) NOT NULL,"
               "    Mass DECIMAL(7, 7) NOT NULL,"
               "  PRIMARY KEY (TubeID)"
               ");"))
TABLES.append(('Setting',
               "CREATE TABLE Setting("
               "    SettingID SERIAL,"
               "    InitialDewPoint DECIMAL(5, 2) NOT NULL,"
               "    InitialDuty DECIMAL(4, 1) NOT NULL,"
               "    InitialMass DECIMAL(7, 7) NOT NULL,"
               "    InitialPressure MEDIUMINT UNSIGNED NOT NULL,"
               "    InitialTemp DECIMAL(5, 2) NOT NULL,"
               "    TimeStep DECIMAL(4, 2) NOT NULL,"
               "  PRIMARY KEY (SettingID)"
               ");"))
TABLES.append(('Test',
               "CREATE TABLE Test("
               "    TestID SERIAL,"
               "    Author VARCHAR(30) NOT NULL,"
               "    DateTime DATETIME NOT NULL,"
               "    Description VARCHAR(500) NOT NULL,"
               "    SettingID BIGINT UNSIGNED NOT NULL,"
               "    TubeID TINYINT UNSIGNED NOT NULL,"
               "  PRIMARY KEY (TestID),"
               "  FOREIGN KEY (SettingID) REFERENCES Setting(SettingID)"
               "    ON UPDATE CASCADE ON DELETE RESTRICT,"
               "  FOREIGN KEY (TubeID) REFERENCES Tube(TubeID)"
               "    ON UPDATE CASCADE ON DELETE RESTRICT"
               ");"))
TABLES.append(('Observation',
               "CREATE TABLE Observation("
               "    ObservationID SERIAL,"
               "    CapManOk TINYINT(1) NOT NULL,"
               "    DewPoint DECIMAL(5, 2) NOT NULL,"
               "    Duty DECIMAL(4, 1) NOT NULL,"
               "    Idx SMALLINT UNSIGNED NOT NULL,"
               "    Mass DECIMAL(7, 7) NOT NULL,"
               "    OptidewOk TINYINT(1) NOT NULL,"
               "    PowOut DECIMAL(6, 4) NOT NULL,"
               "    PowRef DECIMAL(6, 4) NOT NULL,"
               "    Pressure MEDIUMINT UNSIGNED NOT NULL,"
               "    TestID BIGINT UNSIGNED NOT NULL,"
               "  PRIMARY KEY (ObservationID),"
               "  FOREIGN KEY (TestID) REFERENCES Test(TestID)"
               "    ON UPDATE CASCADE ON DELETE RESTRICT"
               ");"))
TABLES.append(('TempObservation',
               "CREATE TABLE TempObservation("
               "    TempObservationID SERIAL,"
               "    Temperature DECIMAL(5, 2) NOT NULL,"
               "    ThermocoupleNum TINYINT(2) UNSIGNED NOT NULL,"
               "    ObservationID BIGINT UNSIGNED NOT NULL,"
               "  PRIMARY KEY (TempObservationID),"
               "  FOREIGN KEY (ObservationID) REFERENCES Observation(ObservationID)"
               "    ON UPDATE CASCADE ON DELETE RESTRICT"
               ");"))

TABLE_NAME_LIST = [table[0] for table in reversed(TABLES)]

SETTINGS_TEST_1 = {'InitialDewPoint': 100,
                   'InitialDuty': 100,
                   'InitialMass': 0.07,
                   'InitialPressure': 100000,
                   'InitialTemp': 290,
                   'TimeStep': 1}

SETTINGS_TEST_2 = {'InitialDewPoint': 500,
                   'InitialDuty': 1000,
                   'InitialMass': 20,
                   'InitialPressure': 8,
                   'InitialTemp': 400,
                   'TimeStep': 20}

TDMS_01_SETTING = {'InitialDewPoint': '292.50',
                   'InitialDuty': '0.0',
                   'InitialMass': '-0.0658138',
                   'InitialPressure': 99977,
                   'InitialTemp': '297.09',
                   'TimeStep': '1.00'}

TDMS_TEST_FILES = [getcwd() + "/tests/data_transfer_test_files/tdms_test_files/tdms_test_file_01.tdms",
                   getcwd() + "/tests/data_transfer_test_files/tdms_test_files/test_tdms_folder_2/tdms_test_file_02.tdms",
                   getcwd() + "/tests/data_transfer_test_files/tdms_test_files/test_tdms_folder_2/tdms_test_file_03.tdms"]

LIST_TDMS_TEST_DIR = getcwd() + "/tests/data_transfer_test_files"

CORRECT_FILE_LIST = [getcwd() + "/tests/data_transfer_test_files/test.tdms",
                     getcwd() + "/tests/data_transfer_test_files/full_test_folder/unit_test_01.tdms",
                     getcwd() + "/tests/data_transfer_test_files/unit_test_02.tdms",
                     getcwd() + "/tests/data_transfer_test_files/unit_test_03.tdms"]

INCORRECT_FILE_LIST = [getcwd() + "/tests/data_transfer_test_files/py.tdmstest",
                       getcwd() + "/tests/data_transfer_test_files/py.tdmstest.py",
                       getcwd() + "/tests/data_transfer_test_files/full_test_folder/unit_test_01.tdms_index",
                       getcwd() + "/tests/data_transfer_test_files/unit_test_02.tdms_index",
                       getcwd() + "/tests/data_transfer_test_files/unit_test_03.tdms_index"]

TDMS_01_DICT_TESTS = {'Author': "ADL",
                      'DateTime': datetime(2017, 8, 3, 19, 33, 9, 217290, pytz.UTC),
                      'Description': ("This is at room temperature, pressure, no laser power, study"
                                      " of boundy development.")}

TDMS_01_OBS_08 = {'CapManOk': 1,
                  'DewPoint': '292.43',
                  'Duty': '0.0',
                  'Idx': 8,
                  'Mass': '-0.0658138',
                  'OptidewOk': 1,
                  'PowOut': '-0.0010',
                  'PowRef': '-0.0015',
                  'Pressure': 99982}

TEST_INDEX = 7

TDMS_01_THM_07 = '296.76'

TC_INDEX = 7

TEST_DIRECTORY = getcwd() + "/tests/data_transfer_test_files/tdms_test_files/"
