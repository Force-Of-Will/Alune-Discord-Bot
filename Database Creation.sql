CREATE DATABASE AluneBot;
USE AluneBot;
CREATE TABLE `ServerActivity` (
	`GuildID` INT NOT NULL,
	`UserID` INT NOT NULL,
	`DateLastActive` DATE NOT NULL,
	PRIMARY KEY (`UserID`)
);

CREATE TABLE `User` (
	`UserID` INT NOT NULL,
    `Username` VARCHAR (32) NOT NULL,
    PRIMARY KEY (`UserID`)
);