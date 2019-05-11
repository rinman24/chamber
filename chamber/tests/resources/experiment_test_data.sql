USE `experimental`;

-- -----------------------------------------------------
-- Table `experimental`.`Pools`
-- -----------------------------------------------------
INSERT INTO `experimental`.`Pools` 
            (`InnerDiameter`, 
             `OuterDiameter`, 
             `Height`, 
             `Material`, 
             `Mass`) 
VALUES      (0.03, 
             0.04, 
             0.06, 
             'Delrin', 
             0.05678);

-- -----------------------------------------------------
-- Table `experimental`.`Settings`
-- -----------------------------------------------------
INSERT INTO `experimental`.`Settings` 
            (`Duty`, 
             `Pressure`, 
             `Temperature`, 
             `TimeStep`) 
VALUES      (0, 
             101325, 
             300, 
             1);

-- -----------------------------------------------------
-- Table `experimental`.`Experiments`
-- -----------------------------------------------------
INSERT INTO `experimental`.`Experiments` 
            (`Author`,
             `DateTime`,
             `Description`,
             `Pools_PoolId`,
             `Settings_SettingId`) 
VALUES      ('RHI',
             '2019-9-24 7:45:00',
             'The description is descriptive.',
             1,
             1);

-- -----------------------------------------------------
-- Table `experimental`.`Observations`
-- -----------------------------------------------------
INSERT INTO `experimental`.`Observations` 
            (`CapManOk`,
             `DewPoint`,
             `Idx`,
             `Mass`,
             `OptidewOk`,
             `Pressure`,
             `Experiments_ExperimentId`)
VALUES      (1,
             280,
             0,
             0.999,
             1,
             101325,
             1);
INSERT INTO `experimental`.`Observations` 
            (`CapManOk`,
             `DewPoint`,
             `Idx`,
             `Mass`,
             `OptidewOk`,
             `Pressure`,
             `Experiments_ExperimentId`)
VALUES      (1,
             281,
             1,
             0.998,
             1,
             101324,
             1);
INSERT INTO `experimental`.`Observations` 
            (`CapManOk`,
             `DewPoint`,
             `Idx`,
             `Mass`,
             `OptidewOk`,
             `Pressure`,
             `Experiments_ExperimentId`)
VALUES      (1,
             282,
             2,
             0.997,
             1,
             101323,
             1);

-- -----------------------------------------------------
-- Table `experimental`.`Temperatures`
-- -----------------------------------------------------
INSERT INTO `experimental`.`Temperatures` 
            (`ThermocoupleNum`,
             `Temperature`,
             `Observations_Idx`,
             `Observations_Experiments_ExperimentId`)
VALUES      (0,
             290,
             0,
             1);
INSERT INTO `experimental`.`Temperatures` 
            (`ThermocoupleNum`,
             `Temperature`,
             `Observations_Idx`,
             `Observations_Experiments_ExperimentId`)
VALUES      (1,
             290.2,
             0,
             1);
INSERT INTO `experimental`.`Temperatures` 
            (`ThermocoupleNum`,
             `Temperature`,
             `Observations_Idx`,
             `Observations_Experiments_ExperimentId`)
VALUES      (0,
             291,
             1,
             1);
INSERT INTO `experimental`.`Temperatures` 
            (`ThermocoupleNum`,
             `Temperature`,
             `Observations_Idx`,
             `Observations_Experiments_ExperimentId`)
VALUES      (1,
             291.2,
             1,
             1);
INSERT INTO `experimental`.`Temperatures` 
            (`ThermocoupleNum`,
             `Temperature`,
             `Observations_Idx`,
             `Observations_Experiments_ExperimentId`)
VALUES      (0,
             292,
             2,
             1);
INSERT INTO `experimental`.`Temperatures` 
            (`ThermocoupleNum`,
             `Temperature`,
             `Observations_Idx`,
             `Observations_Experiments_ExperimentId`)
VALUES      (1,
             292.2,
             2,
             1);
