CREATE DATABASE AluneBot;
USE AluneBot;
CREATE TABLE `User` (
	`UserID` VARCHAR (32) NOT NULL,
    `Username` VARCHAR (32) NOT NULL,
    PRIMARY KEY (`UserID`)
);

CREATE TABLE `ServerActivity` (
	`GuildID` VARCHAR (32) NOT NULL,
	`UserID` VARCHAR (32) NOT NULL,
	`DateLastActive` DATE NOT NULL,
	FOREIGN KEY (`UserID`) REFERENCES `User`(`UserID`)
);