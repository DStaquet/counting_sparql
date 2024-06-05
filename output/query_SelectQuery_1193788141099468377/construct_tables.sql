CREATE TABLE IF NOT EXISTS BGP_2732790592149769836 (
	p1 VARCHAR(255),
	propertyTextual VARCHAR(255),
	product VARCHAR(255),
	label VARCHAR(255),
	k_count INT,
	PRIMARY KEY (p1,propertyTextual,product,label)
);
DROP TABLE IF EXISTS delta_BGP_2732790592149769836;
CREATE TABLE IF NOT EXISTS delta_BGP_2732790592149769836 (
	p1 VARCHAR(255),
	propertyTextual VARCHAR(255),
	product VARCHAR(255),
	label VARCHAR(255),
	k_count INT,
	PRIMARY KEY (p1,propertyTextual,product,label)
);
CREATE TABLE IF NOT EXISTS nu_BGP_2732790592149769836 (
	p1 VARCHAR(255),
	propertyTextual VARCHAR(255),
	product VARCHAR(255),
	label VARCHAR(255),
	k_count INT,
	PRIMARY KEY (p1,propertyTextual,product,label)
);
CREATE TABLE IF NOT EXISTS Filter_4062382548913049243 (
	label VARCHAR(255),
	p1 VARCHAR(255),
	product VARCHAR(255),
	propertyTextual VARCHAR(255),
	k_count INT,
	PRIMARY KEY (p1,propertyTextual,product,label)
);
DROP TABLE IF EXISTS delta_Filter_4062382548913049243;
CREATE TABLE IF NOT EXISTS delta_Filter_4062382548913049243 (
	label VARCHAR(255),
	p1 VARCHAR(255),
	product VARCHAR(255),
	propertyTextual VARCHAR(255),
	k_count INT,
	PRIMARY KEY (p1,propertyTextual,product,label)
);
CREATE TABLE IF NOT EXISTS nu_Filter_4062382548913049243 (
	label VARCHAR(255),
	p1 VARCHAR(255),
	product VARCHAR(255),
	propertyTextual VARCHAR(255),
	k_count INT,
	PRIMARY KEY (p1,propertyTextual,product,label)
);
CREATE TABLE IF NOT EXISTS BGP_2020790532000715027 (
	p2 VARCHAR(255),
	propertyTextual VARCHAR(255),
	product VARCHAR(255),
	label VARCHAR(255),
	k_count INT,
	PRIMARY KEY (p2,propertyTextual,product,label)
);
DROP TABLE IF EXISTS delta_BGP_2020790532000715027;
CREATE TABLE IF NOT EXISTS delta_BGP_2020790532000715027 (
	p2 VARCHAR(255),
	propertyTextual VARCHAR(255),
	product VARCHAR(255),
	label VARCHAR(255),
	k_count INT,
	PRIMARY KEY (p2,propertyTextual,product,label)
);
CREATE TABLE IF NOT EXISTS nu_BGP_2020790532000715027 (
	p2 VARCHAR(255),
	propertyTextual VARCHAR(255),
	product VARCHAR(255),
	label VARCHAR(255),
	k_count INT,
	PRIMARY KEY (p2,propertyTextual,product,label)
);
CREATE TABLE IF NOT EXISTS Filter_5934684086086804418 (
	label VARCHAR(255),
	p2 VARCHAR(255),
	product VARCHAR(255),
	propertyTextual VARCHAR(255),
	k_count INT,
	PRIMARY KEY (p2,propertyTextual,product,label)
);
DROP TABLE IF EXISTS delta_Filter_5934684086086804418;
CREATE TABLE IF NOT EXISTS delta_Filter_5934684086086804418 (
	label VARCHAR(255),
	p2 VARCHAR(255),
	product VARCHAR(255),
	propertyTextual VARCHAR(255),
	k_count INT,
	PRIMARY KEY (p2,propertyTextual,product,label)
);
CREATE TABLE IF NOT EXISTS nu_Filter_5934684086086804418 (
	label VARCHAR(255),
	p2 VARCHAR(255),
	product VARCHAR(255),
	propertyTextual VARCHAR(255),
	k_count INT,
	PRIMARY KEY (p2,propertyTextual,product,label)
);
CREATE TABLE IF NOT EXISTS Union_6291923553636737850 (
	label VARCHAR(255),
	p1 VARCHAR(255),
	p2 VARCHAR(255),
	product VARCHAR(255),
	propertyTextual VARCHAR(255),
	k_count INT,
	PRIMARY KEY (product,label,p2,propertyTextual,p1)
);
DROP TABLE IF EXISTS delta_Union_6291923553636737850;
CREATE TABLE IF NOT EXISTS delta_Union_6291923553636737850 (
	label VARCHAR(255),
	p1 VARCHAR(255),
	p2 VARCHAR(255),
	product VARCHAR(255),
	propertyTextual VARCHAR(255),
	k_count INT,
	PRIMARY KEY (product,label,p2,propertyTextual,p1)
);
CREATE TABLE IF NOT EXISTS nu_Union_6291923553636737850 (
	label VARCHAR(255),
	p1 VARCHAR(255),
	p2 VARCHAR(255),
	product VARCHAR(255),
	propertyTextual VARCHAR(255),
	k_count INT,
	PRIMARY KEY (product,label,p2,propertyTextual,p1)
);
CREATE TABLE IF NOT EXISTS Project_4311502299989220311 (
	label VARCHAR(255),
	product VARCHAR(255),
	propertyTextual VARCHAR(255),
	k_count INT,
	PRIMARY KEY (product,label,propertyTextual)
);
DROP TABLE IF EXISTS delta_Project_4311502299989220311;
CREATE TABLE IF NOT EXISTS delta_Project_4311502299989220311 (
	label VARCHAR(255),
	product VARCHAR(255),
	propertyTextual VARCHAR(255),
	k_count INT,
	PRIMARY KEY (product,label,propertyTextual)
);
CREATE TABLE IF NOT EXISTS nu_Project_4311502299989220311 (
	label VARCHAR(255),
	product VARCHAR(255),
	propertyTextual VARCHAR(255),
	k_count INT,
	PRIMARY KEY (product,label,propertyTextual)
);
CREATE TABLE IF NOT EXISTS SelectQuery_1193788141099468377 (
	label VARCHAR(255),
	product VARCHAR(255),
	propertyTextual VARCHAR(255),
	k_count INT,
	PRIMARY KEY (product,label,propertyTextual)
);
DROP TABLE IF EXISTS delta_SelectQuery_1193788141099468377;
CREATE TABLE IF NOT EXISTS delta_SelectQuery_1193788141099468377 (
	label VARCHAR(255),
	product VARCHAR(255),
	propertyTextual VARCHAR(255),
	k_count INT,
	PRIMARY KEY (product,label,propertyTextual)
);
CREATE TABLE IF NOT EXISTS nu_SelectQuery_1193788141099468377 (
	label VARCHAR(255),
	product VARCHAR(255),
	propertyTextual VARCHAR(255),
	k_count INT,
	PRIMARY KEY (product,label,propertyTextual)
);
