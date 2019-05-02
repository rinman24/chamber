SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

CREATE SCHEMA IF NOT EXISTS `workspace` DEFAULT CHARACTER SET latin1 ;
USE `workspace` ;

CREATE TABLE IF NOT EXISTS `workspace`.`Tube` (`TubeId` TINYINT(3) UNSIGNED NOT NULL AUTO_INCREMENT, `DiameterIn` DECIMAL(7,7) UNSIGNED NOT NULL, `DiameterOut` DECIMAL(7,7) UNSIGNED NOT NULL, `Length` DECIMAL(4,4) UNSIGNED NOT NULL, `Material` VARCHAR(50) NOT NULL, `Mass` DECIMAL(7,7) UNSIGNED NOT NULL, PRIMARY KEY (`TubeId`)) ENGINE = InnoDB AUTO_INCREMENT = 2 DEFAULT CHARACTER SET = latin1;

CREATE TABLE IF NOT EXISTS `workspace`.`Setting` (`SettingId` SMALLINT(3) UNSIGNED NOT NULL AUTO_INCREMENT, `Duty` DECIMAL(4,1) UNSIGNED NOT NULL, `IsMass` BIT(1) NOT NULL, `Pressure` MEDIUMINT(6) UNSIGNED NOT NULL, `Temperature` DECIMAL(4,1) UNSIGNED NOT NULL, `TimeStep` DECIMAL(4,2) UNSIGNED NOT NULL, `Reservoir` BIT(1) NOT NULL, `TubeId` TINYINT(3) UNSIGNED NOT NULL, PRIMARY KEY (`SettingId`, `TubeId`), INDEX `fk_Setting_Tube1_idx` (`TubeId` ASC), CONSTRAINT `fk_Setting_Tube` FOREIGN KEY (`TubeId`) REFERENCES `workspace`.`Tube` (`TubeId`) ON UPDATE CASCADE) ENGINE = InnoDB AUTO_INCREMENT = 16 DEFAULT CHARACTER SET = latin1;

CREATE TABLE IF NOT EXISTS `workspace`.`Test` (`TestId` SMALLINT(3) UNSIGNED NOT NULL AUTO_INCREMENT, `Author` VARCHAR(50) NOT NULL, `DateTime` DATETIME NOT NULL, `Description` VARCHAR(1000) NOT NULL, `SettingId` SMALLINT(3) UNSIGNED NOT NULL, PRIMARY KEY (`TestId`, `SettingId`), INDEX `fk_Test_Setting_idx` (`SettingId` ASC), CONSTRAINT `fk_Test_Setting` FOREIGN KEY (`SettingId`) REFERENCES `workspace`.`Setting` (`SettingId`) ON UPDATE CASCADE) ENGINE = InnoDB AUTO_INCREMENT = 18 DEFAULT CHARACTER SET = latin1;

CREATE TABLE IF NOT EXISTS `workspace`.`Observation` (`CapManOk` BIT(1) NOT NULL, `DewPoint` DECIMAL(5,2) UNSIGNED NOT NULL, `Idx` MEDIUMINT(6) UNSIGNED NOT NULL, `Mass` DECIMAL(7,7) UNSIGNED NULL DEFAULT NULL, `OptidewOk` BIT(1) NOT NULL, `PowOut` DECIMAL(6,4) NULL DEFAULT NULL, `PowRef` DECIMAL(6,4) NULL DEFAULT NULL, `Pressure` MEDIUMINT(6) UNSIGNED NOT NULL, `TestId` SMALLINT(3) UNSIGNED NOT NULL, PRIMARY KEY (`Idx`, `TestId`), INDEX `fk_Observation_Test_idx` (`TestId` ASC), CONSTRAINT `fk_Observation_Test` FOREIGN KEY (`TestId`) REFERENCES `workspace`.`Test` (`TestId`) ON UPDATE CASCADE) ENGINE = InnoDB DEFAULT CHARACTER SET = latin1;

CREATE TABLE IF NOT EXISTS `workspace`.`TempObservation` (`ThermocoupleNum` TINYINT(2) UNSIGNED NOT NULL, `Temperature` DECIMAL(5,2) NOT NULL, `Idx` MEDIUMINT(6) UNSIGNED NOT NULL, `TestId` SMALLINT(3) UNSIGNED NOT NULL, PRIMARY KEY (`Idx`, `TestId`, `ThermocoupleNum`), CONSTRAINT `fk_TempObservation_Observation` FOREIGN KEY (`Idx` , `TestId`) REFERENCES `workspace`.`Observation` (`Idx` , `TestId`) ON UPDATE CASCADE) ENGINE = InnoDB DEFAULT CHARACTER SET = latin1;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
