USE tatmon;
SET NAMES utf8;

CREATE TABLE IF NOT EXISTS raw_rssi_data (
	Longitude DOUBLE NOT NULL,
	Latitude DOUBLE NOT NULL,
	CellID INT NOT NULL,
	ObservedRSSI INT NOT NULL,
	Observations INT NOT NULL,
	PRIMARY KEY (Longitude, Latitude, CellID, ObservedRSSI),
	INDEX (CellID)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS route_rssi_data (
	Route INT NOT NULL,
	Distance DOUBLE NOT NULL,
	CellID INT NOT NULL,
	ObservedRSSI INT NOT NULL,
	Observations INT NOT NULL,
	PRIMARY KEY (Route, Distance, CellID, ObservedRSSI, Observations),
	INDEX (CellID)
) ENGINE=InnoDB;
