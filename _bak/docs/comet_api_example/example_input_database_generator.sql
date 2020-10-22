#Completed 5/23/2016 MJE
# This script builds the database needed for the COMET API results datasets
#
use comet;

#***************************************************************
#*** Build Stored Procedures ***
#***************************************************************
# procedure to modify the fertilizer amount
#***************************************************************
DELIMITER //
DROP PROCEDURE IF EXISTS changeNfert;
CREATE PROCEDURE changeNfert ( 
	IN practice1 VARCHAR( 255 ), 
	IN omad_n_fraction1 FLOAT, 
	IN covercrop_n_fraction1 FLOAT, 
	IN reductionFraction1 FLOAT, 
	IN nfert_eep1 VARCHAR( 15 ) 
) 
BEGIN
	UPDATE 
		comet.planner_cropland_nfert pn 
		JOIN comet.planner_cropland_crops pc ON pn.id_planner_cropland_crops = pc.id 
		JOIN comet.planner_cropland_cps_list pcl ON pc.id_planner_cropland_cps_list = pcl.id 
	SET 
		pn.nfert_amount = pn.nfert_amount * ( 1 - omad_n_fraction1 - covercrop_n_fraction1 ) * reductionFraction1, 
		pn.nfert_eep = nfert_eep1 
	WHERE 
		pcl.practice = practice1 AND 
		pc.current_or_future = 'future' 
	;
END //
DELIMITER ;

#***************************************************************
# procedure to change the tillage
#***************************************************************
DELIMITER //
DROP PROCEDURE IF EXISTS changeTillage;
CREATE PROCEDURE changeTillage ( 
	IN practice1 VARCHAR( 255 ),  
	IN from_tillage_type1 VARCHAR( 25 ),  
	IN to_tillage_type1 VARCHAR( 25 ),  
	IN current_or_future1 VARCHAR( 25 ) 
) 
BEGIN
	UPDATE comet.planner_cropland_tillage pt 
		JOIN comet.planner_cropland_crops pc ON pt.id_planner_cropland_crops = pc.id 
		JOIN comet.planner_cropland_cps_list pcl ON pc.id_planner_cropland_cps_list = pcl.id 
	SET pt.tillage_type = to_tillage_type1 
	WHERE 
		pt.tillage_type = from_tillage_type1 AND 
		pcl.practice = practice1 AND 
		pc.current_or_future = current_or_future1;
END //
DELIMITER ;

#***************************************************************
# procedure to update the nfert eep
#***************************************************************
DELIMITER //
DROP PROCEDURE IF EXISTS changeNfertEEP;
CREATE PROCEDURE changeNfertEEP ( 
	IN practice1 VARCHAR( 255 ),  
	IN nfert_eep1 VARCHAR( 25 ), 
	IN current_or_future1 VARCHAR( 25 ) 
) 
BEGIN
	UPDATE comet.planner_cropland_nfert pn 
		JOIN comet.planner_cropland_crops pc ON pn.id_planner_cropland_crops = pc.id 
		JOIN comet.planner_cropland_cps_list pcl ON pc.id_planner_cropland_cps_list = pcl.id 
	SET pn.nfert_eep = nfert_eep1 
	WHERE 
		pcl.practice = practice1 AND 
		pc.current_or_future = current_or_future1;
END //
DELIMITER ;

#***************************************************************
# procedure to add OMAD events to replace fertilizer events
#***************************************************************
DELIMITER //
DROP PROCEDURE IF EXISTS addOMAD;
CREATE PROCEDURE addOMAD ( 
	IN practice1 VARCHAR( 255 ),  
	IN omad_n_fraction1 FLOAT, 
	IN omad_n_pct1 FLOAT, 
	IN omad_cn_ratio1 FLOAT, 
	IN omad_type1 VARCHAR( 35 ) 
) 
BEGIN
	#Add OMAD
	#1st crop in sequence
	INSERT INTO comet.planner_cropland_omad ( 
		id_planner_cropland_crops, 
		month, 
		day_of_month, 
		day_of_year, 
		omad_type, 
		omad_amount, 
		omad_percent_n, 
		omad_cn_ratio ) 
	SELECT DISTINCT 
		pc.id as 'id_planner_cropland_crops', 
		MONTH( STR_TO_DATE( CONCAT( pc.plant_month1, "/", pc.plant_dayofmonth1, "/2000" ), "%c/%e/%Y" ) ) AS 'month', 
		DAYOFMONTH( STR_TO_DATE( CONCAT( pc.plant_month1, "/", pc.plant_dayofmonth1, "/2000" ), "%c/%e/%Y" ) ) AS 'day_of_month', 
		DAYOFYEAR( STR_TO_DATE( CONCAT( pc.plant_month1, "/", pc.plant_dayofmonth1, "/2000" ), "%c/%e/%Y" ) ) AS 'day_of_year', 
		omad_type1 AS 'omad_type', 
		ROUND( ( IF( pc.irrigated1 = 'Y', IF( ifl.irrig_fert_level IS NULL, ifla.irrig_fert_level, ifl.irrig_fert_level ), IF( ifl.non_irrig_fert_level is null, ifla.non_irrig_fert_level, ifl.non_irrig_fert_level ) ) * omad_cn_ratio1 / 0.5 ) * 0.0044609, 1 ) AS 'omad_amount (short tons/acre)', 
		omad_n_pct1 AS 'omad_percent_n', 
		omad_cn_ratio1 AS 'omad_cn_ratio' 
	FROM 
		comet.planner_cropland_crops pc 
		LEFT JOIN comet.planner_cropland_nfert pn ON pc.id = pn.id_planner_cropland_crops 
		LEFT JOIN comet.planner_cropland_cropname_translation pcct ON pc.cdl_name = pcct.cdl_name 
		LEFT JOIN comet.inventory_fert_levels ifl on pcct.nass_name = ifl.cropname AND pc.statecode = ifl.statecode 
		LEFT JOIN comet.inventory_fert_levels_averages ifla on pcct.nass_name = ifla.cropname 
		LEFT JOIN comet.planner_cropland_cps_list pcl ON pc.id_planner_cropland_cps_list = pcl.id 
	WHERE 
		pn.nfert_amount > 0 AND 
		ifl.yr in ( 1999, 2009 ) AND 
		pcl.practice = practice1 AND 
		pc.current_or_future = 'future' 
	GROUP BY 
		pc.id, 
		MONTH( STR_TO_DATE( CONCAT( pc.plant_month1, "/", pc.plant_dayofmonth1, "/2000" ), "%c/%e/%Y" ) ), 
		DAYOFMONTH( STR_TO_DATE( CONCAT( pc.plant_month1, "/", pc.plant_dayofmonth1, "/2000" ), "%c/%e/%Y" ) ), 
		DAYOFYEAR( STR_TO_DATE( CONCAT( pc.plant_month1, "/", pc.plant_dayofmonth1, "/2000" ), "%c/%e/%Y" ) ) 
	;
END //
DELIMITER ;

#***************************************************************
#***************************************************************
#***************************************************************
# *** Beginning of main script ***
#***************************************************************
#***************************************************************
#***************************************************************

#******************** Build table of practices ********************
DROP TABLE IF EXISTS comet.planner_cropland_cps_list;
CREATE TABLE comet.planner_cropland_cps_list ( 
	id integer auto_increment primary key, 
	irrigated CHAR( 1 ),
	practice varchar( 250 ), 
	index ( practice, irrigated ) );

#irrigated
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Intensive Tillage to No Tillage or Strip Tillage' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Intensive Tillage to Reduced Tillage' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Intensive Tillage to Mulch Tillage' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Intensive Tillage to Ridge Tillage' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Reduced Tillage to No Tillage' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Reduced Tillage to Ridge Tillage' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Reduced Tillage to Mulch Tillage' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Nutrient Management - Improved Nitrogen Fertilizer Management - Use of Slow Release Fertilizers' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Nutrient Management - Improved Nitrogen Fertilizer Management - Use of Nitrification Inhibitors' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Nutrient Management - Improved Nitrogen Fertilizer Management - Fertilizer Reductions' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 10)' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 15)' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 20)' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 25)' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Dairy Manure' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Beef Feedlot Manure' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Other Manure' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Chicken Layer Manure' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Chicken Broiler Manure' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Sheep Manure' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Swine Manure' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Cover Crops - Leguminous' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Cover Crops - Non-leguminous' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Intensive Tillage to No Tillage or Strip Tillage + Nutrient Management - Improved Nitrogen Fertilizer Management - Fertilizer Reductions' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Intensive Tillage to No Tillage or Strip Tillage + non-Leguminous Cover Crops' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Intensive Tillage to No Tillage or Strip Tillage + non-Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 10)' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Intensive Tillage to No Tillage or Strip Tillage + non-Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 15)' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Intensive Tillage to No Tillage or Strip Tillage + non-Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 20)' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Intensive Tillage to No Tillage or Strip Tillage + non-Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 25)' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Intensive Tillage to No Tillage or Strip Tillage + Leguminous Cover Crops' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Intensive Tillage to No Tillage or Strip Tillage + Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 10)' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Intensive Tillage to No Tillage or Strip Tillage + Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 15)' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Intensive Tillage to No Tillage or Strip Tillage + Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 20)' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Intensive Tillage to No Tillage or Strip Tillage + Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 25)' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Conversion to non-legume grassland reserve' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Conversion to grass-legume grassland reserve' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'Y', 'Conversion to grass-legume forage production' );

#non-irrigated
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Intensive Tillage to No Tillage or Strip Tillage' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Intensive Tillage to Reduced Tillage' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Intensive Tillage to Mulch Tillage' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Intensive Tillage to Ridge Tillage' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Reduced Tillage to No Tillage' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Reduced Tillage to Ridge Tillage' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Reduced Tillage to Mulch Tillage' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Nutrient Management - Improved Nitrogen Fertilizer Management - Use of Slow Release Fertilizers' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Nutrient Management - Improved Nitrogen Fertilizer Management - Use of Nitrification Inhibitors' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Nutrient Management - Improved Nitrogen Fertilizer Management - Fertilizer Reductions' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 10)' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 15)' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 20)' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 25)' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Dairy Manure' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Beef Feedlot Manure' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Other Manure' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Chicken Layer Manure' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Chicken Broiler Manure' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Sheep Manure' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Swine Manure' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Cover Crops - Leguminous' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Cover Crops - Non-leguminous' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Intensive Tillage to No Tillage or Strip Tillage + Nutrient Management - Improved Nitrogen Fertilizer Management - Fertilizer Reductions' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Intensive Tillage to No Tillage or Strip Tillage + non-Leguminous Cover Crops' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Intensive Tillage to No Tillage or Strip Tillage + non-Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 10)' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Intensive Tillage to No Tillage or Strip Tillage + non-Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 15)' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Intensive Tillage to No Tillage or Strip Tillage + non-Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 20)' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Intensive Tillage to No Tillage or Strip Tillage + non-Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 25)' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Intensive Tillage to No Tillage or Strip Tillage + Leguminous Cover Crops' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Intensive Tillage to No Tillage or Strip Tillage + Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 10)' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Intensive Tillage to No Tillage or Strip Tillage + Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 15)' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Intensive Tillage to No Tillage or Strip Tillage + Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 20)' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Intensive Tillage to No Tillage or Strip Tillage + Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 25)' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Conversion to non-legume grassland reserve' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Conversion to grass-legume grassland reserve' );
INSERT INTO comet.planner_cropland_cps_list ( irrigated, practice ) VALUES ( 'N', 'Conversion to grass-legume forage production' );

ALTER TABLE comet.planner_cropland_cps_list DROP COLUMN id;
ALTER TABLE comet.planner_cropland_cps_list ORDER BY practice, irrigated;
ALTER TABLE comet.planner_cropland_cps_list ADD COLUMN id INTEGER AUTO_INCREMENT PRIMARY KEY;
ALTER TABLE comet.planner_cropland_cps_list ADD INDEX( practice );

#******************** Build historic management by practice and MLRA ********************
# MLRA Lookup Table:
# MLRA	LRR	non-irrigated						irrigated
#
# 5	A	Non-Irrigated: 2 Yrs Winter Wheat-3 Yrs Clover		Irrigated: Winter Wheat-Corn Silage-Dry Bean
# 14	C	Heavy Utilization, Year-Round (Grazing)			Irrigated: 2 Yrs Cotton-Vegetables-3 Yrs Legume Hay
# 15	C	Heavy Utilization, Year-Round (Grazing)			Irrigated: 2 Yrs Cotton-Vegetables-3 Yrs Legume Hay
# 17	C	Heavy Utilization, Year-Round (Grazing)			Irrigated: 2 Yrs Cotton-Vegetables-3 Yrs Legume Hay
# 21	D	Heavy Utilization, Year-Round (Grazing)			Irrigated: Spring Grain-Sugar Beet
# 22A	D	Heavy Utilization, Year-Round (Grazing)			Irrigated: Spring Grain-Sugar Beet
# 22B	D	Heavy Utilization, Year-Round (Grazing)			Irrigated: Spring Grain-Sugar Beet
# 31	D	Heavy Utilization, Year-Round (Grazing)			Irrigated: Spring Grain-Sugar Beet

# LRR	non-irrigated						irrigated
#
# A	Non-Irrigated: 2 Yrs Winter Wheat-3 Yrs Clover	Irrigated: Winter Wheat-Corn Silage-Dry Bean
# B	Heavy Utilization, Year-Round (Grazing)		Irrigated: Spring Grain-Winter Wheat-Potato
# C	Heavy Utilization, Year-Round (Grazing)		Irrigated: 2 Yrs Cotton-Vegetables-3 Yrs Legume Hay
# DN	Heavy Utilization, Year-Round (Grazing)		Irrigated: Spring Grain-Potato
# DS	Heavy Utilization, Year-Round (Grazing)		Irrigated: Continuous Vegetables
# E	Non-Irrigated: Spring Wheat-Mechanical Fallow	Irrigated: Potato-Small Grain
# F	Non-Irrigated: Spring Wheat-Spring Grain-Fallow	Irrigated: 5 Yrs Legume Hay-Spring Grain
# G	Heavy Utilization, Year-Round (Grazing)		Irrigated: Continuous Corn
# HN	Non-Irrigated: Continuous Winter Wheat		Irrigated: Continuous Corn				
# HS	Non-Irrigated: Continuous Cotton		Irrigated: Continuous Cotton
# IN	Non-Irrigated: Cotton-Winter Wheat		Irrigated: Winter Wheat-Milo-Corn
# IS	Non-Irrigated: Cotton-Winter Wheat		Irrigated: Winter Wheat-Milo-Corn
# J	Non-Irrigated: Continuous Cotton		Non-Irrigated: Continuous Cotton
# K	Non-Irrigated: Corn-Soybean			Non-Irrigated: Corn-Soybean
# L	Non-Irrigated: Corn-Soybean			Non-Irrigated: Corn-Soybean
# M	Non-Irrigated: Corn-Soybean			Non-Irrigated: Corn-Soybean
# N	Non-Irrigated: Corn-Winter Wheat-Soybean	Non-Irrigated: Corn-Winter Wheat-Soybean
# O	Non-Irrigated: Cotton 2 Yrs-Corn		Irrigated: 2 Yrs Rice-2 Yrs Soybean
# PE	Non-Irrigated: Corn-Winter Wheat-Soybean	Non-Irrigated: Corn-Winter Wheat-Soybean
# PW	Non-Irrigated: Corn-Winter Wheat-Soybean	Non-Irrigated: Corn-Winter Wheat-Soybean
# R	Non-Irrigated: 2 Yrs Corn-Soybean		Non-Irrigated: 2 Yrs Corn-Soybean
# S	Non-Irrigated: 2 Yrs Corn-Soybean		Non-Irrigated: 2 Yrs Corn-Soybean
# TE	Non-Irrigated: Corn-Cotton			Irrigated: Corn-Cotton
# TW	Non-Irrigated: Corn-Cotton			Irrigated: Corn-Cotton
# U	Non-Irrigated: Vegetables-Small Grain		Irrigated: Corn Silage-Winter Wheat

#Create the lookup table with the historic management lookups
DROP TABLE IF EXISTS comet.planner_cropland_historic_management_lookup;
CREATE TABLE comet.planner_cropland_historic_management_lookup ( 
	id INTEGER AUTO_INCREMENT PRIMARY KEY, 
	lrr VARCHAR( 2 ), 
	non_irrigated_system VARCHAR( 150 ), 
	irrigated_system VARCHAR( 150 ), 
	INDEX ( lrr ) 
);
INSERT INTO comet.planner_cropland_historic_management_lookup ( lrr, non_irrigated_system, irrigated_system ) VALUES ( 'A', 'Non-Irrigated: 2 Yrs Winter Wheat-3 Yrs Clover', 'Irrigated: Winter Wheat-Corn Silage-Dry Bean' );
INSERT INTO comet.planner_cropland_historic_management_lookup ( lrr, non_irrigated_system, irrigated_system ) VALUES ( 'B', 'Heavy Utilization, Year-Round (Grazing)', 'Irrigated: Spring Grain-Winter Wheat-Potato' );
INSERT INTO comet.planner_cropland_historic_management_lookup ( lrr, non_irrigated_system, irrigated_system ) VALUES ( 'C', 'Heavy Utilization, Year-Round (Grazing)', 'Irrigated: 2 Yrs Cotton-Vegetables-3 Yrs Legume Hay' );
INSERT INTO comet.planner_cropland_historic_management_lookup ( lrr, non_irrigated_system, irrigated_system ) VALUES ( 'DN', 'Heavy Utilization, Year-Round (Grazing)', 'Irrigated: Spring Grain-Potato' );
INSERT INTO comet.planner_cropland_historic_management_lookup ( lrr, non_irrigated_system, irrigated_system ) VALUES ( 'DS', 'Heavy Utilization, Year-Round (Grazing)', 'Irrigated: Continuous Vegetables' );
INSERT INTO comet.planner_cropland_historic_management_lookup ( lrr, non_irrigated_system, irrigated_system ) VALUES ( 'E', 'Non-Irrigated: Spring Wheat-Mechanical Fallow', 'Irrigated: Potato-Small Grain' );
INSERT INTO comet.planner_cropland_historic_management_lookup ( lrr, non_irrigated_system, irrigated_system ) VALUES ( 'F', 'Non-Irrigated: Spring Wheat-Spring Grain-Fallow', 'Irrigated: 5 Yrs Legume Hay-Spring Grain' );
INSERT INTO comet.planner_cropland_historic_management_lookup ( lrr, non_irrigated_system, irrigated_system ) VALUES ( 'G', 'Heavy Utilization, Year-Round (Grazing)', 'Irrigated: Continuous Corn' );
INSERT INTO comet.planner_cropland_historic_management_lookup ( lrr, non_irrigated_system, irrigated_system ) VALUES ( 'HN', 'Non-Irrigated: Continuous Winter Wheat', 'Irrigated: Continuous Corn' );
INSERT INTO comet.planner_cropland_historic_management_lookup ( lrr, non_irrigated_system, irrigated_system ) VALUES ( 'HS', 'Non-Irrigated: Continuous Cotton', 'Irrigated: Continuous Cotton' );
INSERT INTO comet.planner_cropland_historic_management_lookup ( lrr, non_irrigated_system, irrigated_system ) VALUES ( 'IN', 'Non-Irrigated: Cotton-Winter Wheat', 'Irrigated: Winter Wheat-Milo-Corn' );
INSERT INTO comet.planner_cropland_historic_management_lookup ( lrr, non_irrigated_system, irrigated_system ) VALUES ( 'IS', 'Non-Irrigated: Cotton-Winter Wheat', 'Irrigated: Winter Wheat-Milo-Corn' );
INSERT INTO comet.planner_cropland_historic_management_lookup ( lrr, non_irrigated_system, irrigated_system ) VALUES ( 'J', 'Non-Irrigated: Continuous Cotton', 'Non-Irrigated: Continuous Cotton' );
INSERT INTO comet.planner_cropland_historic_management_lookup ( lrr, non_irrigated_system, irrigated_system ) VALUES ( 'K', 'Non-Irrigated: Corn-Soybean', 'Non-Irrigated: Corn-Soybean' );
INSERT INTO comet.planner_cropland_historic_management_lookup ( lrr, non_irrigated_system, irrigated_system ) VALUES ( 'L', 'Non-Irrigated: Corn-Soybean', 'Non-Irrigated: Corn-Soybean' );
INSERT INTO comet.planner_cropland_historic_management_lookup ( lrr, non_irrigated_system, irrigated_system ) VALUES ( 'M', 'Non-Irrigated: Corn-Soybean', 'Non-Irrigated: Corn-Soybean' );
INSERT INTO comet.planner_cropland_historic_management_lookup ( lrr, non_irrigated_system, irrigated_system ) VALUES ( 'N', 'Non-Irrigated: Corn-Winter Wheat-Soybean', 'Non-Irrigated: Corn-Winter Wheat-Soybean' );
INSERT INTO comet.planner_cropland_historic_management_lookup ( lrr, non_irrigated_system, irrigated_system ) VALUES ( 'O', 'Non-Irrigated: Cotton 2 Yrs-Corn', 'Irrigated: 2 Yrs Rice-2 Yrs Soybean' );
INSERT INTO comet.planner_cropland_historic_management_lookup ( lrr, non_irrigated_system, irrigated_system ) VALUES ( 'PE', 'Non-Irrigated: Corn-Winter Wheat-Soybean', 'Non-Irrigated: Corn-Winter Wheat-Soybean' );
INSERT INTO comet.planner_cropland_historic_management_lookup ( lrr, non_irrigated_system, irrigated_system ) VALUES ( 'PW', 'Non-Irrigated: Corn-Winter Wheat-Soybean', 'Non-Irrigated: Corn-Winter Wheat-Soybean' );
INSERT INTO comet.planner_cropland_historic_management_lookup ( lrr, non_irrigated_system, irrigated_system ) VALUES ( 'R', 'Non-Irrigated: 2 Yrs Corn-Soybean', 'Non-Irrigated: 2 Yrs Corn-Soybean' );
INSERT INTO comet.planner_cropland_historic_management_lookup ( lrr, non_irrigated_system, irrigated_system ) VALUES ( 'S', 'Non-Irrigated: 2 Yrs Corn-Soybean', 'Non-Irrigated: 2 Yrs Corn-Soybean' );
INSERT INTO comet.planner_cropland_historic_management_lookup ( lrr, non_irrigated_system, irrigated_system ) VALUES ( 'TE', 'Non-Irrigated: Corn-Cotton', 'Irrigated: Corn-Cotton' );
INSERT INTO comet.planner_cropland_historic_management_lookup ( lrr, non_irrigated_system, irrigated_system ) VALUES ( 'TW', 'Non-Irrigated: Corn-Cotton', 'Irrigated: Corn-Cotton' );
INSERT INTO comet.planner_cropland_historic_management_lookup ( lrr, non_irrigated_system, irrigated_system ) VALUES ( 'U', 'Non-Irrigated: Vegetables-Small Grain', 'Irrigated: Corn Silage-Winter Wheat' );

UPDATE 
	comet.mlra_crops_from_cdl_2009_2015 mcfc 
	JOIN metadata.fips f ON mcfc.fips = f.fips 
SET mcfc.lrr2 = mcfc.lrr 
WHERE mcfc.lrr IN ( "A", "B", "C", "E", "F", "G", "J", "K", "L", "M", "N", "O", "R", "S", "U" );

UPDATE comet.mlra_crops_from_cdl_2009_2015 SET lrr2 = 'PE' WHERE mlra42 = '133A' AND lrr = 'P' AND lrr2 = 'TE';
UPDATE comet.mlra_crops_from_cdl_2009_2015 SET lrr2 = 'PW' WHERE mlra42 = '133B' AND lrr = 'P' AND lrr2 = 'O';
UPDATE comet.mlra_crops_from_cdl_2009_2015 SET lrr2 = 'PE' WHERE mlra42 = '136' AND lrr = 'P' AND lrr2 = 'N';
UPDATE comet.mlra_crops_from_cdl_2009_2015 SET lrr2 = 'TW' WHERE mlra42 = '153A' AND lrr = 'T' AND lrr2 = 'PW';
UPDATE comet.mlra_crops_from_cdl_2009_2015 SET lrr2 = 'TE' WHERE mlra42 = '153B' AND lrr = 'T' AND lrr2 = 'S';
UPDATE comet.mlra_crops_from_cdl_2009_2015 SET lrr2 = 'TE' WHERE mlra42 = '153C' AND lrr = 'T' AND lrr2 = 'S';
UPDATE comet.mlra_crops_from_cdl_2009_2015 SET lrr2 = 'DN' WHERE mlra42 = '22A' AND lrr = 'D' AND lrr2 = 'C';
UPDATE comet.mlra_crops_from_cdl_2009_2015 SET lrr2 = 'DN' WHERE mlra42 = '36' AND lrr = 'D' AND lrr2 = 'E';
UPDATE comet.mlra_crops_from_cdl_2009_2015 SET lrr2 = 'DN' WHERE mlra42 = '42' AND lrr = 'D' AND lrr2 = 'G';
UPDATE comet.mlra_crops_from_cdl_2009_2015 SET lrr2 = 'HN' WHERE mlra42 = '72' AND lrr = 'H' AND lrr2 = 'G';
UPDATE comet.mlra_crops_from_cdl_2009_2015 SET lrr2 = 'HN' WHERE mlra42 = '78A' AND lrr = 'H' AND lrr2 = 'IN';
UPDATE comet.mlra_crops_from_cdl_2009_2015 SET lrr2 = 'HS' WHERE mlra42 = '80A' AND lrr = 'H' AND lrr2 = 'J';
UPDATE comet.mlra_crops_from_cdl_2009_2015 SET lrr2 = 'IS' WHERE mlra42 = '81A' AND lrr = 'I' AND lrr2 = 'HS';

DROP TABLE IF EXISTS mlra42_list;
CREATE TABLE mlra42_list (id INTEGER AUTO_INCREMENT PRIMARY KEY, mlra42 VARCHAR( 5 ), lrr2 VARCHAR( 2 ), INDEX ( mlra42, lrr2 ) );
INSERT INTO mlra42_list ( mlra42, lrr2 ) SELECT DISTINCT mlra42, lrr2 FROM mlra_crops_from_cdl_2009_2015 ORDER BY 1;

UPDATE mlra42_list SET lrr2 = 'PW' WHERE mlra42='133A' AND lrr2='PE';
UPDATE mlra42_list SET lrr2 = 'PW' WHERE mlra42='133A' AND lrr2='PW';
UPDATE mlra42_list SET lrr2 = 'PW' WHERE mlra42='133A' AND lrr2='TW';
UPDATE mlra42_list SET lrr2 = 'PW' WHERE mlra42='133B' AND lrr2='J';
UPDATE mlra42_list SET lrr2 = 'PW' WHERE mlra42='133B' AND lrr2='N';
UPDATE mlra42_list SET lrr2 = 'PW' WHERE mlra42='133B' AND lrr2='PW';
UPDATE mlra42_list SET lrr2 = 'PW' WHERE mlra42='134' AND lrr2='N';
UPDATE mlra42_list SET lrr2 = 'PW' WHERE mlra42='134' AND lrr2='O';
UPDATE mlra42_list SET lrr2 = 'PW' WHERE mlra42='134' AND lrr2='PW';
UPDATE mlra42_list SET lrr2 = 'PW' WHERE mlra42='134' AND lrr2='TW';
UPDATE mlra42_list SET lrr2 = 'PE' WHERE mlra42='136' AND lrr2='PE';
UPDATE mlra42_list SET lrr2 = 'PE' WHERE mlra42='136' AND lrr2='PW';
UPDATE mlra42_list SET lrr2 = 'PE' WHERE mlra42='136' AND lrr2='S';
UPDATE mlra42_list SET lrr2 = 'PE' WHERE mlra42='137' AND lrr2='PE';
UPDATE mlra42_list SET lrr2 = 'PE' WHERE mlra42='137' AND lrr2='PW';
UPDATE mlra42_list SET lrr2 = 'PW' WHERE mlra42='138' AND lrr2='PW';
UPDATE mlra42_list SET lrr2 = 'PW' WHERE mlra42='138' AND lrr2='TW';
UPDATE mlra42_list SET lrr2 = 'PW' WHERE mlra42='138' AND lrr2='U';
UPDATE mlra42_list SET lrr2 = 'TW' WHERE mlra42='150A' AND lrr2='IS';
UPDATE mlra42_list SET lrr2 = 'TW' WHERE mlra42='150A' AND lrr2='J';
UPDATE mlra42_list SET lrr2 = 'TW' WHERE mlra42='150A' AND lrr2='O';
UPDATE mlra42_list SET lrr2 = 'TW' WHERE mlra42='150A' AND lrr2='TW';
UPDATE mlra42_list SET lrr2 = 'IS' WHERE mlra42='150B' AND lrr2='IS';
UPDATE mlra42_list SET lrr2 = 'IS' WHERE mlra42='150B' AND lrr2='TW';
UPDATE mlra42_list SET lrr2 = 'PW' WHERE mlra42='152A' AND lrr2='PW';
UPDATE mlra42_list SET lrr2 = 'PW' WHERE mlra42='152A' AND lrr2='TW';
UPDATE mlra42_list SET lrr2 = 'TE' WHERE mlra42='153A' AND lrr2='PE';
UPDATE mlra42_list SET lrr2 = 'TE' WHERE mlra42='153A' AND lrr2='TE';
UPDATE mlra42_list SET lrr2 = 'TE' WHERE mlra42='153A' AND lrr2='TW';
UPDATE mlra42_list SET lrr2 = 'TE' WHERE mlra42='153A' AND lrr2='U';
UPDATE mlra42_list SET lrr2 = 'TE' WHERE mlra42='153B' AND lrr2='PE';
UPDATE mlra42_list SET lrr2 = 'TE' WHERE mlra42='153B' AND lrr2='PW';
UPDATE mlra42_list SET lrr2 = 'TE' WHERE mlra42='153B' AND lrr2='TE';
UPDATE mlra42_list SET lrr2 = 'TE' WHERE mlra42='153D' AND lrr2='S';
UPDATE mlra42_list SET lrr2 = 'TE' WHERE mlra42='153D' AND lrr2='TE';
UPDATE mlra42_list SET lrr2 = 'A' WHERE mlra42='21' AND lrr2='A';
UPDATE mlra42_list SET lrr2 = 'A' WHERE mlra42='21' AND lrr2='DN';
UPDATE mlra42_list SET lrr2 = 'B' WHERE mlra42='28A' AND lrr2='B';
UPDATE mlra42_list SET lrr2 = 'B' WHERE mlra42='28A' AND lrr2='DN';
UPDATE mlra42_list SET lrr2 = 'B' WHERE mlra42='28A' AND lrr2='E';
UPDATE mlra42_list SET lrr2 = 'DS' WHERE mlra42='30' AND lrr2='C';
UPDATE mlra42_list SET lrr2 = 'DS' WHERE mlra42='30' AND lrr2='DS';
UPDATE mlra42_list SET lrr2 = 'DS' WHERE mlra42='30' AND lrr2='E';
UPDATE mlra42_list SET lrr2 = 'DN' WHERE mlra42='32' AND lrr2='DN';
UPDATE mlra42_list SET lrr2 = 'DN' WHERE mlra42='32' AND lrr2='E';
UPDATE mlra42_list SET lrr2 = 'E' WHERE mlra42='34A' AND lrr2='DN';
UPDATE mlra42_list SET lrr2 = 'E' WHERE mlra42='34A' AND lrr2='E';
UPDATE mlra42_list SET lrr2 = 'DN' WHERE mlra42='34B' AND lrr2='DN';
UPDATE mlra42_list SET lrr2 = 'DN' WHERE mlra42='34B' AND lrr2='E';
UPDATE mlra42_list SET lrr2 = 'DN' WHERE mlra42='35' AND lrr2='DN';
UPDATE mlra42_list SET lrr2 = 'DN' WHERE mlra42='35' AND lrr2='E';
UPDATE mlra42_list SET lrr2 = 'DS' WHERE mlra42='41' AND lrr2='DN';
UPDATE mlra42_list SET lrr2 = 'DS' WHERE mlra42='41' AND lrr2='DS';
UPDATE mlra42_list SET lrr2 = 'DN' WHERE mlra42='42' AND lrr2='DN';
UPDATE mlra42_list SET lrr2 = 'DN' WHERE mlra42='42' AND lrr2='HS';
UPDATE mlra42_list SET lrr2 = 'HN' WHERE mlra42='71' AND lrr2='G';
UPDATE mlra42_list SET lrr2 = 'HN' WHERE mlra42='71' AND lrr2='H';
UPDATE mlra42_list SET lrr2 = 'HN' WHERE mlra42='71' AND lrr2='HN';
UPDATE mlra42_list SET lrr2 = 'HN' WHERE mlra42='71' AND lrr2='M';
UPDATE mlra42_list SET lrr2 = 'HN' WHERE mlra42='72' AND lrr2='HN';
UPDATE mlra42_list SET lrr2 = 'HN' WHERE mlra42='72' AND lrr2='HS';
UPDATE mlra42_list SET lrr2 = 'HN' WHERE mlra42='73' AND lrr2='G';
UPDATE mlra42_list SET lrr2 = 'HN' WHERE mlra42='73' AND lrr2='HN';
UPDATE mlra42_list SET lrr2 = 'HN' WHERE mlra42='73' AND lrr2='HS';
UPDATE mlra42_list SET lrr2 = 'HN' WHERE mlra42='74' AND lrr2='HN';
UPDATE mlra42_list SET lrr2 = 'HN' WHERE mlra42='74' AND lrr2='HS';
UPDATE mlra42_list SET lrr2 = 'HN' WHERE mlra42='75' AND lrr2='HN';
UPDATE mlra42_list SET lrr2 = 'HN' WHERE mlra42='75' AND lrr2='M';
UPDATE mlra42_list SET lrr2 = 'HN' WHERE mlra42='76' AND lrr2='HN';
UPDATE mlra42_list SET lrr2 = 'HN' WHERE mlra42='76' AND lrr2='HS';
UPDATE mlra42_list SET lrr2 = 'HN' WHERE mlra42='76' AND lrr2='J';
UPDATE mlra42_list SET lrr2 = 'HN' WHERE mlra42='76' AND lrr2='M';
UPDATE mlra42_list SET lrr2 = 'HS' WHERE mlra42='77A' AND lrr2='G';
UPDATE mlra42_list SET lrr2 = 'HS' WHERE mlra42='77A' AND lrr2='HN';
UPDATE mlra42_list SET lrr2 = 'HS' WHERE mlra42='77A' AND lrr2='HS';
UPDATE mlra42_list SET lrr2 = 'HS' WHERE mlra42='77B' AND lrr2='G';
UPDATE mlra42_list SET lrr2 = 'HS' WHERE mlra42='77B' AND lrr2='HS';
UPDATE mlra42_list SET lrr2 = 'HS' WHERE mlra42='77C' AND lrr2='G';
UPDATE mlra42_list SET lrr2 = 'HS' WHERE mlra42='77C' AND lrr2='HS';
UPDATE mlra42_list SET lrr2 = 'HS' WHERE mlra42='77C' AND lrr2='IN';
UPDATE mlra42_list SET lrr2 = 'HS' WHERE mlra42='77D' AND lrr2='G';
UPDATE mlra42_list SET lrr2 = 'HS' WHERE mlra42='77D' AND lrr2='HS';
UPDATE mlra42_list SET lrr2 = 'HS' WHERE mlra42='77E' AND lrr2='G';
UPDATE mlra42_list SET lrr2 = 'HS' WHERE mlra42='77E' AND lrr2='HN';
UPDATE mlra42_list SET lrr2 = 'HS' WHERE mlra42='77E' AND lrr2='HS';
UPDATE mlra42_list SET lrr2 = 'HS' WHERE mlra42='78A' AND lrr2='HN';
UPDATE mlra42_list SET lrr2 = 'HS' WHERE mlra42='78A' AND lrr2='HS';
UPDATE mlra42_list SET lrr2 = 'HS' WHERE mlra42='78A' AND lrr2='J';
UPDATE mlra42_list SET lrr2 = 'HS' WHERE mlra42='78C' AND lrr2='HN';
UPDATE mlra42_list SET lrr2 = 'HS' WHERE mlra42='78C' AND lrr2='HS';
UPDATE mlra42_list SET lrr2 = 'HN' WHERE mlra42='79' AND lrr2='HN';
UPDATE mlra42_list SET lrr2 = 'HN' WHERE mlra42='79' AND lrr2='HS';
UPDATE mlra42_list SET lrr2 = 'HS' WHERE mlra42='80A' AND lrr2='HN';
UPDATE mlra42_list SET lrr2 = 'HS' WHERE mlra42='80A' AND lrr2='HS';
UPDATE mlra42_list SET lrr2 = 'HS' WHERE mlra42='80B' AND lrr2='HS';
UPDATE mlra42_list SET lrr2 = 'HS' WHERE mlra42='80B' AND lrr2='IN';
UPDATE mlra42_list SET lrr2 = 'HS' WHERE mlra42='80B' AND lrr2='J';
UPDATE mlra42_list SET lrr2 = 'IS' WHERE mlra42='81A' AND lrr2='HN';
UPDATE mlra42_list SET lrr2 = 'IS' WHERE mlra42='81A' AND lrr2='IN';
UPDATE mlra42_list SET lrr2 = 'IS' WHERE mlra42='81A' AND lrr2='IS';
UPDATE mlra42_list SET lrr2 = 'HN' WHERE mlra42='81B' AND lrr2='HN';
UPDATE mlra42_list SET lrr2 = 'HN' WHERE mlra42='81B' AND lrr2='HS';
UPDATE mlra42_list SET lrr2 = 'HN' WHERE mlra42='81B' AND lrr2='IN';
UPDATE mlra42_list SET lrr2 = 'J' WHERE mlra42='81C' AND lrr2='IN';
UPDATE mlra42_list SET lrr2 = 'J' WHERE mlra42='81C' AND lrr2='IS';
UPDATE mlra42_list SET lrr2 = 'J' WHERE mlra42='81C' AND lrr2='J';
UPDATE mlra42_list SET lrr2 = 'IS' WHERE mlra42='83A' AND lrr2='IS';
UPDATE mlra42_list SET lrr2 = 'IS' WHERE mlra42='83A' AND lrr2='J';
UPDATE mlra42_list SET lrr2 = 'IS' WHERE mlra42='83A' AND lrr2='TW';

#create the historic and modern management table
DROP TABLE IF EXISTS comet.planner_cropland_historic_and_modern_management;
CREATE TABLE comet.planner_cropland_historic_and_modern_management ( 
	id INTEGER AUTO_INCREMENT PRIMARY KEY, 
	cps_id INTEGER, 
	mlra VARCHAR( 5 ), 
	historic_management_name VARCHAR( 150 ), 
	modern_management_name VARCHAR( 150 ) );

INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Intensive Tillage to No Tillage or Strip Tillage' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Intensive Tillage to Reduced Tillage' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Intensive Tillage to Mulch Tillage' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Intensive Tillage to Ridge Tillage' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Reduced Tillage to No Tillage' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Reduced Tillage to Ridge Tillage' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Reduced Tillage to Mulch Tillage' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Nutrient Management - Improved Nitrogen Fertilizer Management - Use of Slow Release Fertilizers' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Nutrient Management - Improved Nitrogen Fertilizer Management - Use of Nitrification Inhibitors' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Nutrient Management - Improved Nitrogen Fertilizer Management - Fertilizer Reductions' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 10)' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 15)' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 20)' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 25)' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Dairy Manure' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Beef Feedlot Manure' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Other Manure' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Chicken Layer Manure' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Chicken Broiler Manure' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Sheep Manure' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Swine Manure' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Cover Crops - Leguminous' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Cover Crops - Non-leguminous' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Intensive Tillage to No Tillage or Strip Tillage + Nutrient Management - Improved Nitrogen Fertilizer Management - Fertilizer Reductions' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Intensive Tillage to No Tillage or Strip Tillage + non-Leguminous Cover Crops' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Intensive Tillage to No Tillage or Strip Tillage + non-Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 10)' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Intensive Tillage to No Tillage or Strip Tillage + non-Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 15)' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Intensive Tillage to No Tillage or Strip Tillage + non-Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 20)' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Intensive Tillage to No Tillage or Strip Tillage + non-Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 25)' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Intensive Tillage to No Tillage or Strip Tillage + Leguminous Cover Crops' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Intensive Tillage to No Tillage or Strip Tillage + Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 10)' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Intensive Tillage to No Tillage or Strip Tillage + Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 15)' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Intensive Tillage to No Tillage or Strip Tillage + Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 20)' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Intensive Tillage to No Tillage or Strip Tillage + Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 25)' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Conversion to non-legume grassland reserve' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Conversion to grass-legume grassland reserve' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;
INSERT INTO comet.planner_cropland_historic_and_modern_management ( cps_id, mlra, historic_management_name, modern_management_name ) SELECT DISTINCT pcl.id, mcfc.mlra42, IF( pcl.irrigated = 'Y', 'Irrigation (Pre 1980s)', 'Upland Non-Irrigated (Pre 1980s)' ), IF( pcl.irrigated = 'Y', phml.irrigated_system, phml.non_irrigated_system  ) FROM comet.planner_cropland_cps_list pcl, comet.mlra42_list mcfc, comet.planner_cropland_historic_management_lookup phml WHERE pcl.practice = 'Conversion to grass-legume forage production' AND mcfc.lrr2 = phml.lrr ORDER BY mcfc.mlra42, pcl.id;

#******************** Build the planner cdl_name lookup table ******
DROP TABLE IF EXISTS comet.planner_cropland_cdl_name_lookup;
CREATE TABLE comet.planner_cropland_cdl_name_lookup ( Id INTEGER AUTO_INCREMENT PRIMARY KEY, cdl_name VARCHAR( 20 ), systemtype VARCHAR( 10 ), cdl_crop1 VARCHAR( 20 ), cdl_crop2 VARCHAR( 20 ), index( cdl_name ), index( cdl_crop1 ), index( cdl_crop2 ) );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'alfalfa', 'summercrop', 'alfalfa', '' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'barley', 'summercrop', 'barley', '' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'corn', 'summercrop', 'corn', '' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'cotton', 'summercrop', 'cotton', '' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'dbl_barley_corn', 'doublecrop', 'winter barley', 'corn' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'dbl_barley_sorghum', 'doublecrop', 'winter barley', 'sorghum' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'dbl_oats_corn', 'doublecrop', 'winter oats', 'corn' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'dbl_winwht_corn', 'doublecrop', 'winter wheat', 'corn' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'dbl_winwht_cotton', 'doublecrop', 'winter wheat', 'cotton' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'dbl_winwht_sorghum', 'doublecrop', 'winter wheat', 'sorghum' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'dbl_winwht_soy', 'doublecrop', 'winter wheat', 'soybeans' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'dry field beans', 'summercrop', 'dry field beans', '' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'fallow', 'summercrop', 'fallow', '' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'grass_clover mix', 'summercrop', 'grass_clover mix', '' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'grass_hay', 'summercrop', 'grass_hay', '' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'grass', 'summercrop', 'grass_hay', '' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'grass_pasture', 'summercrop', 'grass_pasture', '' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'millet', 'summercrop', 'millet', '' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'NoData', 'summercrop', 'NoData', '' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'oats', 'summercrop', 'oats', '' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'peanut', 'summercrop', 'peanut', '' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'potato', 'summercrop', 'potato', '' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'rice_flooded', 'summercrop', 'rice_flooded', '' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'rye', 'summercrop', 'rye', '' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'sorghum', 'summercrop', 'sorghum', '' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'soybeans', 'summercrop', 'soybeans', '' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'spring wheat', 'summercrop', 'spring wheat', '' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'sugar beets', 'summercrop', 'sugar beets', '' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'sunflower', 'summercrop', 'sunflower', '' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'switchgrass', 'summercrop', 'switchgrass', '' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'tomatoes', 'summercrop', 'tomatoes', '' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'winter wheat', 'wintercrop', 'winter wheat', 'winter wheat' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'winter barley', 'wintercrop', 'winter barley', 'winter barley' );
INSERT INTO comet.planner_cropland_cdl_name_lookup ( cdl_name, systemtype, cdl_crop1, cdl_crop2 ) VALUES ( 'winter oats', 'wintercrop', 'winter oats', 'winter oats' );
	
#******************** Build planner_cropland_crops Table ********************
DROP TABLE IF EXISTS comet.planner_cropland_crops;
CREATE TABLE comet.planner_cropland_crops (
	id INTEGER AUTO_INCREMENT PRIMARY KEY,
	id_planner_cropland_cps_list INTEGER,
	statecode CHAR( 2 ),
	sequence VARCHAR( 35 ),
	current_or_future VARCHAR( 7 ),
	cdl_name VARCHAR( 18 ),
	cropname1 VARCHAR( 18 ),
	cfarm_cropname1 VARCHAR( 25 ),
	irrigated1 CHAR( 1 ), 
	plant_month1 VARCHAR( 2 ),
	plant_dayofmonth1 VARCHAR( 2 ),
	plant_dayofyear1 VARCHAR( 3 ),
	harv_month1 VARCHAR( 2 ),
	harv_dayofmonth1 VARCHAR( 2 ),
	harv_dayofyear1 VARCHAR( 3 ),
	pltm_or_frst1 CHAR( 4 ),
	INDEX ( statecode, cdl_name, cropname1, irrigated1 ),
	INDEX ( id_planner_cropland_cps_list )
);

#create a lookup table for crops
DROP TABLE IF EXISTS comet.state_crop_list;
CREATE TABLE comet.state_crop_list (
	id INTEGER AUTO_INCREMENT PRIMARY KEY, 
	state CHAR( 2 ), 
	sequence CHAR( 10 ), 
	cdl_name VARCHAR( 18 ) 
);
INSERT INTO comet.state_crop_list ( state, sequence, cdl_name ) 
	SELECT DISTINCT mcfc.state, 'summercrop', mcfc.summer_crop_2009 FROM comet.mlra_crops_from_cdl_2009_2015 mcfc WHERE mcfc.summer_crop_2009 NOT IN ( 'NoData' ) AND mcfc.summer_crop_2009 != '' AND mcfc.summer_crop_2009 IS NOT NULL UNION 
	SELECT DISTINCT mcfc.state, 'summercrop', mcfc.summer_crop_2010 FROM comet.mlra_crops_from_cdl_2009_2015 mcfc WHERE mcfc.summer_crop_2010 NOT IN ( 'NoData' ) AND mcfc.summer_crop_2010 != '' AND mcfc.summer_crop_2010 IS NOT NULL UNION 
	SELECT DISTINCT mcfc.state, 'summercrop', mcfc.summer_crop_2011 FROM comet.mlra_crops_from_cdl_2009_2015 mcfc WHERE mcfc.summer_crop_2011 NOT IN ( 'NoData' ) AND mcfc.summer_crop_2011 != '' AND mcfc.summer_crop_2011 IS NOT NULL UNION 
	SELECT DISTINCT mcfc.state, 'summercrop', mcfc.summer_crop_2012 FROM comet.mlra_crops_from_cdl_2009_2015 mcfc WHERE mcfc.summer_crop_2012 NOT IN ( 'NoData' ) AND mcfc.summer_crop_2012 != '' AND mcfc.summer_crop_2012 IS NOT NULL UNION 
	SELECT DISTINCT mcfc.state, 'summercrop', mcfc.summer_crop_2013 FROM comet.mlra_crops_from_cdl_2009_2015 mcfc WHERE mcfc.summer_crop_2013 NOT IN ( 'NoData' ) AND mcfc.summer_crop_2013 != '' AND mcfc.summer_crop_2013 IS NOT NULL UNION 
	SELECT DISTINCT mcfc.state, 'summercrop', mcfc.summer_crop_2014 FROM comet.mlra_crops_from_cdl_2009_2015 mcfc WHERE mcfc.summer_crop_2014 NOT IN ( 'NoData' ) AND mcfc.summer_crop_2014 != '' AND mcfc.summer_crop_2014 IS NOT NULL UNION 
	SELECT DISTINCT mcfc.state, 'summercrop', mcfc.summer_crop_2015 FROM comet.mlra_crops_from_cdl_2009_2015 mcfc WHERE mcfc.summer_crop_2015 NOT IN ( 'NoData' ) AND mcfc.summer_crop_2015 != '' AND mcfc.summer_crop_2015 IS NOT NULL UNION 
	SELECT DISTINCT mcfc.state, 'wintercrop', mcfc.winter_crop_2008_2009 FROM comet.mlra_crops_from_cdl_2009_2015 mcfc WHERE mcfc.winter_crop_2008_2009 NOT IN ( 'NoData' ) AND mcfc.winter_crop_2008_2009 != '' AND mcfc.winter_crop_2008_2009 IS NOT NULL UNION 
	SELECT DISTINCT mcfc.state, 'wintercrop', mcfc.winter_crop_2009_2010 FROM comet.mlra_crops_from_cdl_2009_2015 mcfc WHERE mcfc.winter_crop_2009_2010 NOT IN ( 'NoData' ) AND mcfc.winter_crop_2009_2010 != '' AND mcfc.winter_crop_2009_2010 IS NOT NULL UNION 
	SELECT DISTINCT mcfc.state, 'wintercrop', mcfc.winter_crop_2010_2011 FROM comet.mlra_crops_from_cdl_2009_2015 mcfc WHERE mcfc.winter_crop_2010_2011 NOT IN ( 'NoData' ) AND mcfc.winter_crop_2010_2011 != '' AND mcfc.winter_crop_2010_2011 IS NOT NULL UNION 
	SELECT DISTINCT mcfc.state, 'wintercrop', mcfc.winter_crop_2011_2012 FROM comet.mlra_crops_from_cdl_2009_2015 mcfc WHERE mcfc.winter_crop_2011_2012 NOT IN ( 'NoData' ) AND mcfc.winter_crop_2011_2012 != '' AND mcfc.winter_crop_2011_2012 IS NOT NULL UNION 
	SELECT DISTINCT mcfc.state, 'wintercrop', mcfc.winter_crop_2012_2013 FROM comet.mlra_crops_from_cdl_2009_2015 mcfc WHERE mcfc.winter_crop_2012_2013 NOT IN ( 'NoData' ) AND mcfc.winter_crop_2012_2013 != '' AND mcfc.winter_crop_2012_2013 IS NOT NULL UNION 
	SELECT DISTINCT mcfc.state, 'wintercrop', mcfc.winter_crop_2013_2014 FROM comet.mlra_crops_from_cdl_2009_2015 mcfc WHERE mcfc.winter_crop_2013_2014 NOT IN ( 'NoData' ) AND mcfc.winter_crop_2013_2014 != '' AND mcfc.winter_crop_2013_2014 IS NOT NULL UNION 
	SELECT DISTINCT mcfc.state, 'wintercrop', mcfc.winter_crop_2014_2015 FROM comet.mlra_crops_from_cdl_2009_2015 mcfc WHERE mcfc.winter_crop_2014_2015 NOT IN ( 'NoData' ) AND mcfc.winter_crop_2014_2015 != '' AND mcfc.winter_crop_2014_2015 IS NOT NULL ORDER BY 1, 3;
	
INSERT INTO comet.state_crop_list ( state, sequence, cdl_name ) VALUES ( 'CA', 'summercrop', 'grass_hay' );
	
#Build the list of all possible crops for each CPS and insert them into the planner_cropland_crops table
INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Intensive Tillage to No Tillage or Strip Tillage' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Intensive Tillage to Reduced Tillage' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Intensive Tillage to Mulch Tillage' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Intensive Tillage to Ridge Tillage' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Reduced Tillage to No Tillage' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Reduced Tillage to Ridge Tillage' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Reduced Tillage to Mulch Tillage' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Nutrient Management - Improved Nitrogen Fertilizer Management - Use of Slow Release Fertilizers' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Nutrient Management - Improved Nitrogen Fertilizer Management - Use of Nitrification Inhibitors' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Nutrient Management - Improved Nitrogen Fertilizer Management - Fertilizer Reductions' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 10)' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 15)' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 20)' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 25)' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Dairy Manure' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Beef Feedlot Manure' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Other Manure' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Chicken Layer Manure' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Chicken Broiler Manure' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Sheep Manure' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Swine Manure' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Cover Crops - Leguminous' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Cover Crops - Non-leguminous' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Intensive Tillage to No Tillage or Strip Tillage + Nutrient Management - Improved Nitrogen Fertilizer Management - Fertilizer Reductions' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Intensive Tillage to No Tillage or Strip Tillage + non-Leguminous Cover Crops' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Intensive Tillage to No Tillage or Strip Tillage + non-Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 10)' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Intensive Tillage to No Tillage or Strip Tillage + non-Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 15)' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Intensive Tillage to No Tillage or Strip Tillage + non-Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 20)' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Intensive Tillage to No Tillage or Strip Tillage + non-Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 25)' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Intensive Tillage to No Tillage or Strip Tillage + Leguminous Cover Crops' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Intensive Tillage to No Tillage or Strip Tillage + Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 10)' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Intensive Tillage to No Tillage or Strip Tillage + Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 15)' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Intensive Tillage to No Tillage or Strip Tillage + Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 20)' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Intensive Tillage to No Tillage or Strip Tillage + Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 25)' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Conversion to non-legume grassland reserve' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Conversion to grass-legume grassland reserve' ORDER BY 1, 2, 5;

INSERT INTO comet.planner_cropland_crops ( id_planner_cropland_cps_list, statecode, sequence, current_or_future, cdl_name ) 
SELECT DISTINCT pcl.id, mcfc.state, sequence, 'current', mcfc.cdl_name FROM comet.planner_cropland_cps_list pcl, comet.state_crop_list mcfc WHERE pcl.practice = 'Conversion to grass-legume forage production' ORDER BY 1, 2, 5;

DELETE FROM planner_cropland_crops WHERE cdl_name = 'NoData' OR cdl_name = '' OR cdl_name IS NULL;

UPDATE comet.planner_cropland_crops SET cdl_name = 'soybeans' WHERE cdl_name = 'soy';

UPDATE comet.planner_cropland_crops SET cfarm_cropname1 = cropname1;
UPDATE comet.planner_cropland_crops SET cropname1 = 'winter wheat'  WHERE cdl_name = 'winter wheat';
UPDATE comet.planner_cropland_crops SET cropname1 = 'oats'  WHERE cdl_name = 'winter oats';
UPDATE comet.planner_cropland_crops SET cropname1 = 'barley'  WHERE cdl_name = 'winter barley';

UPDATE comet.planner_cropland_crops SET cfarm_cropname1 = 'oats'  WHERE cdl_name = 'winter oats';
UPDATE comet.planner_cropland_crops SET cfarm_cropname1 = 'barley'  WHERE cdl_name = 'winter barley';

UPDATE comet.planner_cropland_crops SET cfarm_cropname1 = 'alfalfa' where cdl_name = 'alfalfa';
UPDATE comet.planner_cropland_crops SET cfarm_cropname1 = 'barley' WHERE cdl_name = 'barley';
UPDATE comet.planner_cropland_crops SET cfarm_cropname1 = 'corn' WHERE cdl_name = 'corn';
UPDATE comet.planner_cropland_crops SET cfarm_cropname1 = 'cotton' WHERE cdl_name = 'cotton';
UPDATE comet.planner_cropland_crops SET cfarm_cropname1 = 'dry field beans' WHERE cdl_name = 'dry field beans';
UPDATE comet.planner_cropland_crops SET cfarm_cropname1 = 'fallow' WHERE cdl_name = 'fallow';
UPDATE comet.planner_cropland_crops SET cfarm_cropname1 = 'grass' WHERE cdl_name = 'grass';
UPDATE comet.planner_cropland_crops SET cfarm_cropname1 = 'grass-legume mix' WHERE cdl_name = 'grass_clover mix';
UPDATE comet.planner_cropland_crops SET cfarm_cropname1 = 'grass' WHERE cdl_name = 'grass_hay';
UPDATE comet.planner_cropland_crops SET cfarm_cropname1 = 'grass' WHERE cdl_name = 'grass_pasture';
UPDATE comet.planner_cropland_crops SET cfarm_cropname1 = 'millet' WHERE cdl_name = 'millet';
UPDATE comet.planner_cropland_crops SET cfarm_cropname1 = 'oats' WHERE cdl_name = 'oats';
UPDATE comet.planner_cropland_crops SET cfarm_cropname1 = 'orchard_vine' WHERE cdl_name = 'orchard_vine';
UPDATE comet.planner_cropland_crops SET cfarm_cropname1 = 'peanut' WHERE cdl_name = 'peanut';
UPDATE comet.planner_cropland_crops SET cfarm_cropname1 = 'potato' WHERE cdl_name = 'potato';
UPDATE comet.planner_cropland_crops SET cfarm_cropname1 = 'rice - flooded' WHERE cdl_name = 'rice_flooded';
UPDATE comet.planner_cropland_crops SET cfarm_cropname1 = 'rye' WHERE cdl_name = 'rye';
UPDATE comet.planner_cropland_crops SET cfarm_cropname1 = 'sorghum' WHERE cdl_name = 'sorghum';
UPDATE comet.planner_cropland_crops SET cfarm_cropname1 = 'soybean' WHERE cdl_name = 'soybeans';
UPDATE comet.planner_cropland_crops SET cfarm_cropname1 = 'spring wheat' WHERE cdl_name = 'spring wheat';
UPDATE comet.planner_cropland_crops SET cfarm_cropname1 = 'sugar beets' WHERE cdl_name = 'sugar beets';
UPDATE comet.planner_cropland_crops SET cfarm_cropname1 = 'sunflower' WHERE cdl_name = 'sunflower';
UPDATE comet.planner_cropland_crops SET cfarm_cropname1 = 'switchgrass' WHERE cdl_name = 'switchgrass';
UPDATE comet.planner_cropland_crops SET cfarm_cropname1 = 'tomatoes' WHERE cdl_name = 'tomatoes';
UPDATE comet.planner_cropland_crops SET cfarm_cropname1 = 'winter wheat' WHERE cdl_name = 'winter wheat';

UPDATE comet.crop_planting_harvest_dates SET cdl_name = 'soybeans' WHERE cropcode = 'SYBN';
# remove the potato planting dates, etc. for all but 'potatoes, summer' as CDL doesn't distinguish between them
DELETE FROM comet.crop_planting_harvest_dates WHERE cropname IN ( 'Potatoes, all', 'Potatoes, fall', 'Potatoes, spring' );
DELETE FROM comet.crop_planting_harvest_dates_averages WHERE cropname IN ( 'Potatoes, all', 'Potatoes, fall', 'Potatoes, spring' );

#Create a lookup table holding the crop_planting_harvest_date average months for the entire United States:
DROP TABLE IF EXISTS comet.crop_planting_harvest_dates_averages;
CREATE TABLE comet.crop_planting_harvest_dates_averages 
( 
	id INTEGER AUTO_INCREMENT PRIMARY KEY,
	cropcode VARCHAR( 7 ),
	cropname VARCHAR( 25 ),
	cdl_name VARCHAR( 25 ),
	cdl_name2 VARCHAR( 25 ), 
	nass_name VARCHAR( 25 ),
	plant_month_start_avg SMALLINT, 
	plant_dayofmonth_start_avg SMALLINT,
	plant_dayofyear_start_avg MEDIUMINT,
	harv_month_start_avg SMALLINT, 
	harv_dayofmonth_start_avg SMALLINT,
	harv_dayofyear_start_avg MEDIUMINT, 
	plant_month_end_avg SMALLINT, 
	plant_dayofmonth_end_avg SMALLINT,
	plant_dayofyear_end_avg MEDIUMINT,
	harv_month_end_avg SMALLINT, 
	harv_dayofmonth_end_avg SMALLINT,
	harv_dayofyear_end_avg MEDIUMINT, 
	plant_month_avg SMALLINT, 
	plant_dayofmonth_avg SMALLINT,
	plant_dayofyear_avg MEDIUMINT,
	harv_month_avg SMALLINT, 
	harv_dayofmonth_avg SMALLINT,
	harv_dayofyear_avg MEDIUMINT, 
	INDEX ( cdl_name )
);

INSERT INTO comet.crop_planting_harvest_dates_averages ( 
	cropcode, 
	cropname, 
	cdl_name, 
	cdl_name2, 
	nass_name, 
	plant_month_avg, 
	plant_dayofmonth_avg, 
	plant_dayofyear_avg, 
	harv_month_avg, 
	harv_dayofmonth_avg, 
	harv_dayofyear_avg 
) 
SELECT DISTINCT 
	cropcode, 
	cropname, 
	cdl_name, 
	cdl_name2, 
	nass_name, 
	MONTH( MAKEDATE( 2000, TRUNCATE( AVG( DAYOFYEAR( plant_start ) ), 0 ) ) ) AS plant_start_month_avg, 
	DAYOFMONTH( MAKEDATE( 2000, TRUNCATE( AVG( DAYOFYEAR( plant_start ) ), 0 ) ) ) AS plant_start_dom_avg, 
	ROUND( AVG( DAYOFYEAR( plant_start ) ), 0 ) AS plant_start_doy_avg, 
	MONTH( MAKEDATE( 2000, TRUNCATE( AVG( DAYOFYEAR( harv_start ) ), 0 ) ) ) AS harv_start_month_avg, 
	DAYOFMONTH( MAKEDATE( 2000, TRUNCATE( AVG( DAYOFYEAR( harv_start ) ), 0 ) ) ) AS harv_start_dom_avg, 
	ROUND( AVG( DAYOFYEAR( harv_start ) ), 0 ) AS harv_start_doy_avg, 
	MONTH( MAKEDATE( 2000, TRUNCATE( AVG( DAYOFYEAR( plant_end ) ), 0 ) ) ) AS plant_end_month_avg, 
	DAYOFMONTH( MAKEDATE( 2000, TRUNCATE( AVG( DAYOFYEAR( plant_end ) ), 0 ) ) ) AS plant_end_dom_avg, 
	ROUND( AVG( DAYOFYEAR( plant_end ) ), 0 ) AS plant_end_doy_avg, 
	MONTH( MAKEDATE( 2000, TRUNCATE( AVG( DAYOFYEAR( harv_end ) ), 0 ) ) ) AS harv_end_month_avg, 
	DAYOFMONTH( MAKEDATE( 2000, TRUNCATE( AVG( DAYOFYEAR( harv_end ) ), 0 ) ) ) AS harv_end_dom_avg, 
	ROUND( AVG( DAYOFYEAR( harv_end ) ), 0 ) AS harv_end_doy_avg, 
	MONTH( MAKEDATE( 2000, TRUNCATE( AVG( DAYOFYEAR( plant_median ) ), 0 ) ) ) AS plant_median_month_avg, 
	DAYOFMONTH( MAKEDATE( 2000, TRUNCATE( AVG( DAYOFYEAR( plant_median ) ), 0 ) ) ) AS plant_median_dom_avg, 
	ROUND( AVG( DAYOFYEAR( plant_median ) ), 0 ) AS plant_median_doy_avg, 
	MONTH( MAKEDATE( 2000, TRUNCATE( AVG( DAYOFYEAR( harv_median ) ), 0 ) ) ) AS harv_median_month_avg, 
	DAYOFMONTH( MAKEDATE( 2000, TRUNCATE( AVG( DAYOFYEAR( harv_median ) ), 0 ) ) ) AS harv_median_dom_avg, 
	ROUND( AVG( DAYOFYEAR( harv_median ) ), 0 ) AS harv_median_doy_avg 
FROM comet.crop_planting_harvest_dates 
GROUP BY 1,2,3,4,5 
ORDER BY 1,2,3,4,5;

# add in the 'grass' crop, based on the 'grass_hay' crop
insert into comet.crop_planting_harvest_dates_averages (
	cropname, 
	cdl_name, 
	cdl_name2, 
	nass_name, 
	plant_month_start_avg, 
	plant_dayofmonth_start_avg, 
	plant_dayofyear_start_avg, 
	harv_month_start_avg, 
	harv_dayofmonth_start_avg, 
	harv_dayofyear_start_avg, 
	plant_month_end_avg, 
	plant_dayofmonth_end_avg, 
	plant_dayofyear_end_avg, 
	harv_month_end_avg, 
	harv_dayofmonth_end_avg, 
	harv_dayofyear_end_avg, 
	plant_month_avg, 
	plant_dayofmonth_avg, 
	plant_dayofyear_avg, 
	harv_month_avg, 
	harv_dayofmonth_avg, 
	harv_dayofyear_avg ) 
SELECT 
	'grass', 
	'grass', 
	'grass', 
	'grass', 
	plant_month_start_avg, 
	plant_dayofmonth_start_avg, 
	plant_dayofyear_start_avg, 
	harv_month_start_avg, 
	harv_dayofmonth_start_avg, 
	harv_dayofyear_start_avg, 
	plant_month_end_avg, 
	plant_dayofmonth_end_avg, 
	plant_dayofyear_end_avg, 
	harv_month_end_avg, 
	harv_dayofmonth_end_avg, 
	harv_dayofyear_end_avg, 
	plant_month_avg, 
	plant_dayofmonth_avg, 
	plant_dayofyear_avg, 
	harv_month_avg, 
	harv_dayofmonth_avg, 
	harv_dayofyear_avg 
FROM comet.crop_planting_harvest_dates_averages where cropname = 'grass_hay';

# Update the base date records with the national-level data
UPDATE 
	comet.planner_cropland_crops pc 
	JOIN comet.planner_cropland_cps_list pcl ON pc.id_planner_cropland_cps_list = pcl.id 
	JOIN comet.planner_cropland_cdl_name_lookup pcnl ON pc.cdl_name = pcnl.cdl_name 
	JOIN comet.crop_planting_harvest_dates_averages cphd ON pcnl.cdl_crop1 = cphd.cdl_name 
SET 
	pc.cropname1 = pcnl.cdl_crop1, 
	pc.irrigated1 = pcl.irrigated, 
	pc.plant_month1 = cphd.plant_month_avg, 
	pc.plant_dayofmonth1 = 15, 
	pc.plant_dayofyear1 = cphd.plant_dayofyear_avg, 
	pc.harv_month1 = cphd.harv_month_avg, 
	pc.harv_dayofmonth1 = 15, 
	pc.harv_dayofyear1 = cphd.harv_dayofyear_avg, 
	pc.pltm_or_frst1 = 'pltm';

# Update the base date records with the state data where it exists
UPDATE 
	comet.planner_cropland_crops pc 
	JOIN comet.planner_cropland_cps_list pcl ON pc.id_planner_cropland_cps_list = pcl.id 
	JOIN comet.planner_cropland_cdl_name_lookup pcnl ON pc.cdl_name = pcnl.cdl_name 
	JOIN comet.crop_planting_harvest_dates cphd ON pcnl.cdl_crop1 = cphd.cdl_name AND pc.statecode = cphd.statecode 
SET 
	pc.cropname1 = pcnl.cdl_crop1, 
	pc.irrigated1 = pcl.irrigated, 
	pc.plant_month1 = MONTH( cphd.plant_median ), 
	pc.plant_dayofmonth1 = DAYOFMONTH( cphd.plant_median ), 
	pc.plant_dayofyear1 = cphd.plant_median_dayofyear, 
	pc.harv_month1 = MONTH( cphd.harv_median ), 
	pc.harv_dayofmonth1 = DAYOFMONTH( cphd.harv_median ), 
	pc.harv_dayofyear1 = cphd.harv_median_dayofyear, 
	pc.pltm_or_frst1 = 'pltm';

#Update the irrigation status for these crops
UPDATE 
	comet.planner_cropland_crops pc 
	JOIN comet.planner_cropland_cps_list pcl ON pc.id_planner_cropland_cps_list = pcl.id 
SET 
	pc.irrigated1 = pcl.irrigated;

#Add in the Future Management Crops
INSERT INTO comet.planner_cropland_crops ( 	
	id_planner_cropland_cps_list, 
	statecode, 
	sequence, 
	current_or_future, 
	cdl_name, 
	cropname1, 
	cfarm_cropname1, 
	irrigated1, 
	plant_month1,
	plant_dayofmonth1, 
	plant_dayofyear1, 
	harv_month1, 
	harv_dayofmonth1, 
	harv_dayofyear1, 
	pltm_or_frst1 
) 
SELECT DISTINCT 
	id_planner_cropland_cps_list, 
	statecode, 
	sequence, 
	'future', 
	cdl_name, 
	cropname1, 
	cfarm_cropname1, 
	irrigated1, 
	plant_month1,
	plant_dayofmonth1, 
	plant_dayofyear1, 
	harv_month1, 
	harv_dayofmonth1, 
	harv_dayofyear1, 
	pltm_or_frst1 
FROM comet.planner_cropland_crops;

#**** update the forage planting crop name ****
SET @practice = 'Conversion to grass-legume forage production';
UPDATE 
	comet.planner_cropland_crops pc 
	JOIN comet.planner_cropland_cps_list pcl ON pc.id_planner_cropland_cps_list = pcl.id 
SET 
	cdl_name = 'grass_hay',
	cropname1 = 'grass_hay',
	cfarm_cropname1 = 'Grass-Legume Mix',
	pltm_or_frst1 = 'frst', 
	plant_month1 = 1, 
	plant_dayofmonth1 = 3, 
	plant_dayofyear1 = 3 
WHERE 
	pcl.practice = @practice 
	AND current_or_future = 'future';

#******************** Build the crop name translation table ********************
DROP TABLE IF EXISTS comet.planner_cropland_cropname_translation;
CREATE TABLE comet.planner_cropland_cropname_translation (
	id INTEGER AUTO_INCREMENT PRIMARY KEY, 
	cdl_name VARCHAR( 25 ),
	nass_name VARCHAR( 25 ), 
	INDEX ( cdl_name ), 
	INDEX ( nass_name ) );

INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'alfalfa', 'Hay, alfalfa' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'barley', 'Barley, spring' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'corn', 'Corn For Grain' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'cotton', 'Cotton, all' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'dbl_barley_corn', 'Barley, fall' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'dbl_barley_corn', 'Corn for Grain' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'dbl_barley_sorghum', 'Barley, fall' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'dbl_barley_sorghum', 'Sorghum for Grain' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'dbl_oats_corn', 'Oats, fall' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'dbl_oats_corn', 'Corn for Grain' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'dbl_winwht_corn', 'Wheat, Winter' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'dbl_winwht_corn', 'Corn for Grain' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'dbl_winwht_cotton', 'Wheat, Winter' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'dbl_winwht_cotton', 'Cotton, All' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'dbl_winwht_sorghum', 'Wheat, Winter' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'dbl_winwht_sorghum', 'Sorghum For Grain' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'dbl_winwht_soy', 'Wheat, Winter' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'dbl_winwht_soy', 'Soybeans' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'dry field beans', 'Beans, Dry Edible' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'fallow', 'fallow' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'grass_clover mix', 'Hay, other' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'grass_hay', 'Hay, other' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'grass', 'Hay, other' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'grass_pasture', 'Hay, other' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'millet', 'Sorghum for Grain' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'oats', 'Oats, spring' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'peanut', 'Peanuts' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'potato', 'Potatoes, summer' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'rice_flooded', 'Rice, all' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'rye', 'Rye' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'sorghum', 'Sorghum for Grain' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'soybeans', 'Soybeans' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'spring wheat', 'Wheat, spring' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'durum wheat', 'Wheat, Durum' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'sugar beets', 'Sugarbeets' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'sunflower', 'Sunflower, all' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'switchgrass', 'Hay, other' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'tomatoes', 'Corn for Grain' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'winter wheat', 'Wheat, winter' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'winter barley', 'Barley, fall' );
INSERT INTO comet.planner_cropland_cropname_translation ( cdl_name, nass_name ) VALUES ( 'winter oats', 'Oats, fall' );

#***********************************************************
#*** Reset the perennial crop plant start date to January 1 ***
#***********************************************************

UPDATE comet.planner_cropland_crops 
SET 
	plant_month1 = 1, 
	plant_dayofmonth1 = 3, 
	plant_dayofyear1 = 3, 
	pltm_or_frst1 = 'frst' 
WHERE 
	cdl_name = 'alfalfa' or cdl_name like '%grass%';

#******************** Build Harvest Table ********************
DROP TABLE IF EXISTS comet.planner_cropland_harvests;
CREATE TABLE comet.planner_cropland_harvests (
	id INTEGER AUTO_INCREMENT PRIMARY KEY,
	id_planner_cropland_crops INTEGER,
	month SMALLINT,
	day_of_month SMALLINT,
	day_of_year SMALLINT,
	number_of_harvests SMALLINT, 
	grain VARCHAR( 3 ), 
	yield FLOAT,
	strawstoverhayremoval SMALLINT, 
	index (id_planner_cropland_crops )
);

#grain harvests
INSERT INTO comet.planner_cropland_harvests ( 
	id_planner_cropland_crops, 
	number_of_harvests, 
	month,
	day_of_month,
	day_of_year, 
	grain, 
	yield, 
	strawstoverhayremoval ) 
SELECT DISTINCT 
	pc.id as 'id_planner_cropland_crops', 
	1 as 'number_of_harvests', 
	pc.harv_month1 AS 'month', 
	pc.harv_dayofmonth1 AS 'day_of_month', 
	pc.harv_dayofyear1 AS 'day_of_year', 
	'Yes' AS 'grain', 
	IF( ROUND( AVG( nrd.value ), IF( CAST( AVG( nrd.value ) AS INTEGER ) < 10, 1, 0 ) ) is null, 
	ROUND( AVG( nrda.value ), IF( CAST( AVG( nrda.value ) AS INTEGER ) < 10, 1, 0 ) ), 
	ROUND( AVG( nrd.value ), IF( CAST( AVG( nrd.value ) AS INTEGER ) < 10, 1, 0 ) ) ) AS 'yield', 
	0 AS 'strawstoverhayremoval' 
FROM 
	comet.planner_cropland_crops pc 
	LEFT JOIN comet.planner_cropland_cropname_translation pcct ON pc.cdl_name = pcct.cdl_name 
	LEFT JOIN comet.nass_raw_data nrd ON pc.statecode = nrd.statecode AND pcct.nass_name = nrd.cropname 
	LEFT JOIN comet.nass_raw_data_averages nrda ON pcct.nass_name = nrda.cropname 
WHERE 
	pc.cropname1 NOT IN ( 'grass_legume mix', 'grass_clover mix', 'grass_hay', 'alfalfa', 'grass_pasture' ) 
GROUP BY 
	pc.id,
	pc.harv_month1, 
	pc.harv_dayofmonth1, 
	pc.harv_dayofyear1 
;

# Hay Harvests
# Add a harvest on the 1st day of harvest season, and for up to six additional harvests after that
DROP PROCEDURE IF EXISTS addHayHarvests;
DELIMITER //
CREATE PROCEDURE addHayHarvests()
BEGIN
	DECLARE x INT;
	SET x = 0;
	WHILE x < 7 DO
		INSERT INTO comet.planner_cropland_harvests ( id_planner_cropland_crops, number_of_harvests, month, day_of_month, day_of_year, grain, yield, strawstoverhayremoval ) 
		SELECT DISTINCT 
			pc.id as 'id_planner_cropland_crops', 
			( if( cphd.harv_end is null, cphda.harv_dayofyear_end_avg, DAYOFYEAR( cphd.harv_end ) ) - if( cphd.harv_start is null, cphda.harv_dayofyear_start_avg, DAYOFYEAR( cphd.harv_start ) ) ) / 45 AS 'number_of_harvests', 
			MONTH( ADDDATE( cphd.harv_start, 45 * x ) ) as 'month', 
			DAYOFMONTH( ADDDATE( cphd.harv_start, 45 * x ) ) as 'day_of_month', 
			DAYOFYEAR( ADDDATE( cphd.harv_start, 45 * x ) ) as 'day_of_year', 
			'No' AS 'grain', 
			ROUND( AVG( IF( nrd.value IS NULL, nrda.value, nrd.value ) ), IF( CAST( AVG( nrda.value ) AS INTEGER ) < 20, 1, 0 ) ) AS 'yield', 
			50 AS 'strawstoverhayremoval' 
		FROM comet.crop_planting_harvest_dates cphd 
		LEFT JOIN car2017.crop_planting_harvest_dates_averages cphda ON cphd.cdl_name = cphda.cdl_name 
		LEFT JOIN comet.planner_cropland_crops pc ON cphd.statecode = pc.statecode AND cphd.cdl_name = pc.cropname1 
		LEFT JOIN comet.nass_raw_data nrd ON cphd.statecode = nrd.statecode AND cphd.nass_name = nrd.cropname 
		LEFT JOIN comet.nass_raw_data_averages nrda ON cphd.nass_name = nrda.cropname 
		WHERE pc.cropname1 IN ( 'grass_legume mix', 'grass_clover mix', 'grass_hay', 'alfalfa' ) AND ( DAYOFYEAR( cphd.harv_end ) - DAYOFYEAR( cphd.harv_start ) ) / 45 > x 
		GROUP BY 
			pc.id, 
			( if( cphd.harv_end is null, cphda.harv_dayofyear_end_avg, DAYOFYEAR( cphd.harv_end ) ) - if( cphd.harv_start is null, cphda.harv_dayofyear_start_avg, DAYOFYEAR( cphd.harv_start ) ) ) / 45, 
			MONTH( ADDDATE( if( cphd.harv_start is null, CONCAT( cphda.harv_month_start_avg, "/", cphda.harv_dayofmonth_start_avg, "/2000" ), cphd.harv_start ), 45 * x ) ), 
			DAYOFMONTH( ADDDATE( if( cphd.harv_start is null, CONCAT( cphda.harv_month_start_avg, "/", cphda.harv_dayofmonth_start_avg, "/2000" ), cphd.harv_start ), 45 * x ) ), 
			DAYOFYEAR( ADDDATE( if( cphd.harv_start is null, CONCAT( cphda.harv_month_start_avg, "/", cphda.harv_dayofmonth_start_avg, "/2000" ), cphd.harv_start ), 45 * x ) );
		SET x = x + 1;
	END WHILE;
	
	#Add a final harvest on the last day of harvest season
	INSERT INTO comet.planner_cropland_harvests ( id_planner_cropland_crops, number_of_harvests, month, day_of_month, day_of_year, grain, yield, strawstoverhayremoval ) 
	SELECT DISTINCT 
		pc.id as 'id_planner_cropland_crops', 
		( if( cphd.harv_end is null, cphda.harv_dayofyear_end_avg, DAYOFYEAR( cphd.harv_end ) ) - if( cphd.harv_start is null, cphda.harv_dayofyear_start_avg, DAYOFYEAR( cphd.harv_start ) ) ) / 45 AS 'number_of_harvests', 
		MONTH( if( cphd.harv_end is null, CONCAT( cphda.harv_month_end_avg, "/", cphda.harv_dayofmonth_end_avg, "/2000" ), cphd.harv_end ) ) AS 'month', 
		DAYOFMONTH( if( cphd.harv_end is null, CONCAT( cphda.harv_month_end_avg, "/", cphda.harv_dayofmonth_end_avg, "/2000" ), cphd.harv_end ) ) AS 'day_of_month', 
		if( cphd.harv_end is null, cphda.harv_dayofyear_end_avg, DAYOFYEAR( cphd.harv_end ) ) AS 'day_of_year', 
		'No' AS 'grain', 
		ROUND( AVG( IF( nrd.value IS NULL, nrda.value, nrd.value ) ), IF( CAST( AVG( IF( nrd.value IS NULL, nrda.value, nrd.value ) ) AS INTEGER ) < 10, 1, 0 ) ) AS 'yield', 
		50 AS 'strawstoverhayremoval' 
	FROM comet.crop_planting_harvest_dates cphd 
	LEFT JOIN comet.crop_planting_harvest_dates_averages cphda ON cphd.cdl_name = cphda.cdl_name 
	LEFT JOIN comet.planner_cropland_crops pc ON cphd.statecode = pc.statecode AND cphd.cdl_name = pc.cropname1 
	LEFT JOIN comet.nass_raw_data nrd ON cphd.statecode = nrd.statecode AND cphd.nass_name = nrd.cropname 
	LEFT JOIN comet.nass_raw_data_averages nrda ON cphd.nass_name = nrda.cropname 
	WHERE pc.cropname1 IN ( 'grass', 'grass_legume mix', 'grass-legume mix', 'grass_clover mix', 'grass_hay', 'alfalfa', 'switchgrass', 'clover' ) 
	GROUP BY pc.id, ( if( cphd.harv_end is null, cphda.harv_dayofyear_end_avg, DAYOFYEAR( cphd.harv_end ) ) - if( cphd.harv_start is null, cphda.harv_dayofyear_start_avg, DAYOFYEAR( cphd.harv_start ) ) ) / 45, MONTH( if( cphd.harv_end is null, CONCAT( cphda.harv_month_end_avg, "/", cphda.harv_dayofmonth_end_avg, "/2000" ), cphd.harv_end ) ), DAYOFMONTH( if( cphd.harv_end is null, CONCAT( cphda.harv_month_end_avg, "/", cphda.harv_dayofmonth_end_avg, "/2000" ), cphd.harv_end ) ), if( cphd.harv_end is null, cphda.harv_dayofyear_end_avg, DAYOFYEAR( cphd.harv_end ) )
	;
	
END //
DELIMITER ;

CALL addHayHarvests();

#******************** Build Grazing Table ********************
DROP TABLE IF EXISTS comet.planner_cropland_grazing;
CREATE TABLE comet.planner_cropland_grazing (
	id INTEGER AUTO_INCREMENT PRIMARY KEY,
	id_planner_cropland_crops INTEGER,
	start_month SMALLINT,
	start_day_of_month SMALLINT,
	start_day_of_year SMALLINT,
	end_month SMALLINT,
	end_day_of_month SMALLINT,
	end_day_of_year SMALLINT,
	rest_period SMALLINT, 
	utilization_pct SMALLINT, 
	index ( id_planner_cropland_crops )
);

#two grazing periods, 45 day interval, 60% utilization, Jan 1st to May 31st, then Oct 1 to Dec 31st
INSERT INTO comet.planner_cropland_grazing ( id_planner_cropland_crops, start_month, start_day_of_month, start_day_of_year, end_month, end_day_of_month, end_day_of_year, rest_period, utilization_pct ) SELECT DISTINCT pc.id as 'id_planner_cropland_crops', 1 AS 'start_month', 1 AS 'start_day_of_month', 1 AS 'start_day_of_year', 5 AS 'end_month', 31 AS 'end_day_of_month', 151 AS 'end_day_of_year', 45 AS 'rest_period', 60 AS 'utilization_pct' 
FROM comet.crop_planting_harvest_dates cphd 
JOIN comet.planner_cropland_crops pc ON cphd.statecode = pc.statecode AND cphd.cdl_name = pc.cropname1 
JOIN comet.planner_cropland_cps_list pcl ON pc.id_planner_cropland_cps_list = pcl.id 
WHERE pc.cropname1 = 'grass_pasture' GROUP BY pc.id;
	
INSERT INTO comet.planner_cropland_grazing ( id_planner_cropland_crops, start_month, start_day_of_month, start_day_of_year, end_month, end_day_of_month, end_day_of_year, rest_period, utilization_pct ) SELECT DISTINCT pc.id as 'id_planner_cropland_crops', 10 AS 'start_month', 1 AS 'start_day_of_month', 274 AS 'start_day_of_year', 12 AS 'end_month', 31 AS 'end_day_of_month', 365 AS 'end_day_of_year', 45 AS 'rest_period', 60 AS 'utilization_pct' 
FROM comet.crop_planting_harvest_dates cphd 
JOIN comet.planner_cropland_crops pc ON cphd.statecode = pc.statecode AND cphd.cdl_name = pc.cropname1 
JOIN comet.planner_cropland_cps_list pcl ON pc.id_planner_cropland_cps_list = pcl.id 
WHERE pc.cropname1 = 'grass_pasture' GROUP BY pc.id;

#******************** Build Tillage Table ********************
DROP TABLE IF EXISTS comet.planner_cropland_tillage;
CREATE TABLE comet.planner_cropland_tillage (
	id INTEGER AUTO_INCREMENT PRIMARY KEY,
	id_planner_cropland_crops INTEGER,
	month SMALLINT,
	day_of_month SMALLINT,
	day_of_year SMALLINT,
	tillage_type VARCHAR( 50 ), 
	index ( id_planner_cropland_crops )
);

#crop #1
INSERT INTO comet.planner_cropland_tillage ( 
	id_planner_cropland_crops, 
	month, 
	day_of_month, 
	day_of_year, 
	tillage_type ) 
SELECT DISTINCT 
	pc.id as 'id_planner_cropland_crops', 
	MONTH( DATE_SUB( STR_TO_DATE( CONCAT( pc.plant_month1, "/", pc.plant_dayofmonth1, "/2000" ), "%c/%e/%Y" ), INTERVAL 1 DAY ) ) AS 'month', 
	DAYOFMONTH( DATE_SUB( STR_TO_DATE( CONCAT( pc.plant_month1, "/", pc.plant_dayofmonth1, "/2000" ), "%c/%e/%Y" ), INTERVAL 1 DAY ) ) AS 'day_of_month', 
	DAYOFYEAR( DATE_SUB( STR_TO_DATE( CONCAT( pc.plant_month1, "/", pc.plant_dayofmonth1, "/2000" ), "%c/%e/%Y" ), INTERVAL 1 DAY ) ) AS 'day_of_year', 
	'Intensive Tillage' AS 'tillage_type' 
FROM 
	comet.planner_cropland_crops pc 
;

#******************** Build N Fertilization Table ********************
DROP TABLE IF EXISTS comet.planner_cropland_nfert;
CREATE TABLE comet.planner_cropland_nfert (
	id INTEGER AUTO_INCREMENT PRIMARY KEY, 
	id_planner_cropland_crops INTEGER, 
	month SMALLINT,
	day_of_month SMALLINT,
	day_of_year SMALLINT, 
	nfert_type VARCHAR( 50 ), 
	nfert_amount FLOAT, 
	nfert_application_method VARCHAR( 50 ), 
	nfert_eep VARCHAR( 50 ), 
	index ( id_planner_cropland_crops )
);

#Apply 100% of N at time of planting
#1st crop in sequence
INSERT INTO comet.planner_cropland_nfert ( 
	id_planner_cropland_crops, 
	month,
	day_of_month,
	day_of_year, 
	nfert_type, 
	nfert_amount, 
	nfert_application_method, 
	nfert_eep ) 
SELECT DISTINCT 
	pc.id as 'id_planner_cropland_crops', 
	pc.plant_month1 AS 'month', 
	pc.plant_dayofmonth1 AS 'day_of_month', 
	pc.plant_dayofyear1 AS 'day_of_year', 
	'UAN' AS 'nfert_type', 
	ROUND( AVG( IF( pc.irrigated1 = 'Y', IF( ifl.irrig_fert_level IS NULL, ifla.irrig_fert_level, ifl.irrig_fert_level ), IF( ifl.non_irrig_fert_level IS NULL, ifla.non_irrig_fert_level, ifl.non_irrig_fert_level ) ) * 8.92179 ), 1 ), 
	'Surface Band / Sidedress' AS 'nfert_application_method', 
	'None' AS 'nfert_eep' 
FROM 
	comet.planner_cropland_crops pc 
	LEFT JOIN comet.planner_cropland_cropname_translation pcct ON pc.cdl_name = pcct.cdl_name 
	LEFT JOIN comet.inventory_fert_levels ifl on pcct.nass_name = ifl.cropname AND pc.statecode = ifl.statecode 
	LEFT JOIN comet.inventory_fert_levels_averages ifla on pcct.nass_name = ifla.cropname 
WHERE 
	ifl.yr in ( 1999, 2009 ) 
	AND ifla.yr in ( 1999, 2009 ) 
GROUP BY 
	pc.id, 
	DAYOFYEAR( STR_TO_DATE( CONCAT( pc.plant_month1, "/", pc.plant_dayofmonth1, "/2000" ), "%c/%e/%Y" ) ) 
;

#******************** Build OMAD Table ********************
#<OMADApplicationDate>3/1/2001</OMADApplicationDate><OMADType>Compost or Composted Manure</OMADType><OMADAmount>5</OMADAmount>OMADPercentN>2.5</OMADPercentN><OMADCNRatio>12</OMADCNRatio>
DROP TABLE IF EXISTS comet.planner_cropland_omad;
CREATE TABLE comet.planner_cropland_omad (
	id INTEGER AUTO_INCREMENT PRIMARY KEY, 
	id_planner_cropland_crops INTEGER, 
	month SMALLINT,
	day_of_month SMALLINT,
	day_of_year SMALLINT, 
	omad_type VARCHAR( 50 ), 
	omad_amount FLOAT, 
	omad_percent_n FLOAT, 
	omad_cn_ratio FLOAT, 
	index ( id_planner_cropland_crops ) 
);

#******************** Build Irrigation Table ********************
#<IrrigationDate>6/15/2000</IrrigationDate><IrrigationInches>1</IrrigationInches>
DROP TABLE IF EXISTS comet.planner_cropland_irrig;
CREATE TABLE comet.planner_cropland_irrig ( 
	id INTEGER AUTO_INCREMENT PRIMARY KEY, 
	id_planner_cropland_crops INTEGER, 
	number_of_irrig_events SMALLINT, 
	month SMALLINT, 
	day_of_month SMALLINT, 
	day_of_year SMALLINT, 
	irrig_amount FLOAT, 
	index ( id_planner_cropland_crops )
);

#Insert weekly irrigation events, 2.54 cm per week from planting until 2 weeks before harvest, up to 28 total
#grain crops
DROP PROCEDURE IF EXISTS addGrainIrrigation;
DELIMITER //
CREATE PROCEDURE addGrainIrrigation()
BEGIN
	DECLARE x INT;
	SET x = 0;
	WHILE x < 28 DO
		INSERT INTO comet.cropland_irrig ( id_cropland_crops, number_of_irrig_events, month, day_of_month, day_of_year, irrig_amount ) 
		SELECT DISTINCT pc.id as 'id_cropland_crops', ( DAYOFYEAR( STR_TO_DATE( CONCAT( pc.harv_month1, "/", IF( pc.harv_dayofmonth1 = 0, 1, pc.harv_dayofmonth1 ), "/2000" ), "%c/%e/%Y" ) ) - DAYOFYEAR( STR_TO_DATE( CONCAT( pc.plant_month1, "/", if( pc.plant_dayofmonth1 = 0, 1, pc.plant_dayofmonth1 ), "/2000" ), "%c/%e/%Y" ) ) ) / 7 AS 'number_of_irrig_events', MONTH( DATE_ADD( STR_TO_DATE( CONCAT( pc.plant_month1, "/", if( pc.plant_dayofmonth1 = 0, 1, pc.plant_dayofmonth1 ), "/2000" ), "%c/%e/%Y" ), INTERVAL ( x * 7 ) DAY ) ) AS 'month', DAYOFMONTH( DATE_ADD( STR_TO_DATE( CONCAT( pc.plant_month1, "/", if( pc.plant_dayofmonth1 = 0, 1, pc.plant_dayofmonth1 ), "/2000" ), "%c/%e/%Y" ), INTERVAL ( x * 7 ) DAY ) ) AS 'day_of_month', DAYOFYEAR( DATE_ADD( STR_TO_DATE( CONCAT( pc.plant_month1, "/", if( pc.plant_dayofmonth1 = 0, 1, pc.plant_dayofmonth1 ), "/2000" ), "%c/%e/%Y" ), INTERVAL ( x * 7 ) DAY ) ) as 'day_of_year', 2.54 as 'irrig_amount' 
		FROM comet.cropland_crops pc 
		WHERE pc.cropname1 NOT IN ( 'rye', 'winter wheat', 'winter barley', 'winter oats', 'grass', 'grass_legume mix', 'grass-legume mix', 'grass_clover mix', 'grass_hay', 'alfalfa', 'switchgrass', 'clover', 'grass_pasture' ) 
		AND pc.irrigated1 = 'Y' 
		AND ( DAYOFYEAR( STR_TO_DATE( CONCAT( pc.harv_month1, "/", IF( pc.harv_dayofmonth1 = 0, 1, pc.harv_dayofmonth1 ), "/2000" ), "%c/%e/%Y" ) ) - DAYOFYEAR( STR_TO_DATE( CONCAT( pc.plant_month1, "/", if( pc.plant_dayofmonth1 = 0, 1, pc.plant_dayofmonth1 ), "/2000" ), "%c/%e/%Y" ) ) ) / 7 > x;
		SET x = x + 1;
	END WHILE;
END //
DELIMITER ;

CALL addGrainIrrigation();

#Insert weekly irrigation events for winter grains, 2.54 cm per week from planting until 2 weeks before harvest, up to 28 total
#grain crops
DROP PROCEDURE IF EXISTS addWinterGrainIrrigation;
DELIMITER //
CREATE PROCEDURE addWinterGrainIrrigation()
BEGIN
	DECLARE x INT;
	SET x = 0;
	WHILE x < 28 DO
		INSERT INTO car2017.cropland_irrig ( id_cropland_crops, number_of_irrig_events, month, day_of_month, day_of_year, irrig_amount ) 
		SELECT DISTINCT 
		pc.id as 'id_cropland_crops', 
		( DAYOFYEAR( STR_TO_DATE( CONCAT( pc.harv_month1, "/", IF( pc.harv_dayofmonth1 = 0, 1, pc.harv_dayofmonth1 ), "/2000" ), "%c/%e/%Y" ) ) - DAYOFYEAR( STR_TO_DATE( "01/01/2000", "%c/%e/%Y" ) ) ) / 7 AS 'number_of_irrig_events', 
		MONTH( DATE_ADD( STR_TO_DATE( "01/01/2000", "%c/%e/%Y" ), INTERVAL ( x * 7 ) DAY ) ) AS 'month', 
		DAYOFMONTH( DATE_ADD( STR_TO_DATE( "01/01/2000", "%c/%e/%Y" ), INTERVAL ( x * 7 ) DAY ) ) AS 'day_of_month', 
		DAYOFYEAR( DATE_ADD( STR_TO_DATE( "01/01/2000", "%c/%e/%Y" ), INTERVAL ( x * 7 ) DAY ) ) as 'day_of_year', 
		2.54 as 'irrig_amount' 
		FROM comet.cropland_crops pc 
		WHERE pc.cropname1 IN ( 'rye', 'winter wheat', 'winter barley', 'winter oats' ) AND pc.irrigated1 = 'Y' AND ( DAYOFYEAR( STR_TO_DATE( CONCAT( pc.harv_month1, "/", IF( pc.harv_dayofmonth1 = 0, 1, pc.harv_dayofmonth1 ), "/2000" ), "%c/%e/%Y" ) ) - DAYOFYEAR( STR_TO_DATE( "01/01/2000", "%c/%e/%Y" ) ) ) / 7 > x;
		SET x = x + 1;
	END WHILE;
END //
DELIMITER ;

CALL addWinterGrainIrrigation();

#hay crops
# The default Hay irrigation starts on April 1st of every year. 
# We need to work on this to make it more flexible - start it 2 months before the first harvest, but not in the previous calendar year in the case of the SW deserts,
# where hay harvests might begin in February.
DROP PROCEDURE IF EXISTS addHayIrrigation;
DELIMITER //
CREATE PROCEDURE addHayIrrigation()
BEGIN
	DECLARE x INT;
	SET x = 0;
	WHILE x < 53 DO
		INSERT INTO car2017.cropland_irrig ( id_cropland_crops, number_of_irrig_events, month, day_of_month, day_of_year, irrig_amount ) 
		SELECT DISTINCT 
			pc.id as 'id_cropland_crops', 
			( if( cphd.harv_end is null, cphda.harv_dayofyear_end_avg, DAYOFYEAR( cphd.harv_end ) ) - 122 ) / 7 AS 'number_of_irrig_events', 
			MONTH( DATE_ADD( "2000-04-01", INTERVAL ( x * 7 ) DAY ) ) AS 'month', 
			DAYOFMONTH( DATE_ADD( "2000-04-01", INTERVAL ( x * 7 ) DAY ) ) AS 'day_of_month', 
			DAYOFYEAR( DATE_ADD( "2000-04-01", INTERVAL ( x * 7 ) DAY ) ) as 'day_of_year', 
			2.54 as 'irrig_amount' 
		FROM comet.crop_planting_harvest_dates cphd 
		LEFT JOIN car2017.crop_planting_harvest_dates_averages cphda ON cphd.cdl_name = cphda.cdl_name 
		LEFT JOIN car2017.cropland_crops pc ON cphd.statecode = pc.statecode AND cphd.cdl_name = pc.cropname1 
		WHERE 
			pc.cropname1 IN ( 'grass', 'grass_legume mix', 'grass-legume mix', 'grass_clover mix', 'grass_hay', 'alfalfa', 'switchgrass', 'clover', 'grass_pasture' ) 
			AND pc.irrigated1 = 'Y' 
			AND ( if( cphd.harv_end is null, cphda.harv_dayofyear_end_avg, DAYOFYEAR( cphd.harv_end ) ) - 122 ) / 7 > x;
		SET x = x + 1;
	END WHILE;
END //
DELIMITER ;

CALL addHayIrrigation();

#******************** burning ********************
#<Burning>No burning</Burning>
DROP TABLE IF EXISTS comet.planner_cropland_burning;
CREATE TABLE comet.planner_cropland_burning (
	id INTEGER AUTO_INCREMENT PRIMARY KEY, 
	id_planner_cropland_crops INTEGER, 
	month SMALLINT,
	day_of_month SMALLINT,
	day_of_year SMALLINT, 
	burn_type VARCHAR( 50 ), 
	index ( id_planner_cropland_crops )
);

#grain crops
#1st crop in sequence
INSERT INTO comet.planner_cropland_burning ( 
	id_planner_cropland_crops, 
	month, 
	day_of_month, 
	day_of_year, 
	burn_type ) 
SELECT DISTINCT 
	pc.id as 'id_planner_cropland_crops', 
	MONTH( DATE_ADD( STR_TO_DATE( CONCAT( pc.harv_month1, "/", IF( pc.harv_dayofmonth1 = 0, 1, pc.harv_dayofmonth1 ), "/2000" ), "%c/%e/%Y" ), INTERVAL 1 DAY ) ) AS 'month', 
	DAYOFMONTH( DATE_ADD( STR_TO_DATE( CONCAT( pc.harv_month1, "/", IF( pc.harv_dayofmonth1 = 0, 1, pc.harv_dayofmonth1 ), "/2000" ), "%c/%e/%Y" ), INTERVAL 1 DAY ) ) AS 'day_of_month', 
	DAYOFYEAR( DATE_ADD( STR_TO_DATE( CONCAT( pc.harv_month1, "/", IF( pc.harv_dayofmonth1 = 0, 1, pc.harv_dayofmonth1 ), "/2000" ), "%c/%e/%Y" ), INTERVAL 1 DAY ) ) as 'day_of_year', 
	'no burning' as 'burn_type' 
FROM 
	comet.crop_planting_harvest_dates cphd 
	JOIN comet.planner_cropland_crops pc ON cphd.statecode = pc.statecode AND cphd.cdl_name = pc.cropname1
	;

# We don't need to restrict the cropland burning events since the "event" is "no burning"
# hence I'm commenting out the rest of these restrictions. MJE 10/23/2017
#WHERE 
#	pc.cropname1 NOT IN ( 'grass', 'grass_legume mix', 'grass-legume mix', 'grass_clover mix', 'grass_hay', 'alfalfa', 'switchgrass', 'clover', 'grass_pasture' );
#
##hay crops
#INSERT INTO car2017.cropland_burning ( 
#	id_cropland_crops, 
#	month, 
#	day_of_month, 
#	day_of_year, 
#	burn_type ) 
#SELECT DISTINCT 
#	pc.id as 'id_cropland_crops', 
#	MONTH( DATE_ADD( if( cphd.harv_end is null, cphda.harv_end, cphd.harv_end ), INTERVAL 1 DAY ) ) AS 'month', 
#	DAYOFMONTH( DATE_ADD( if( cphd.harv_end is null, cphda.harv_end, cphd.harv_end ), INTERVAL 1 DAY ) ) AS 'day_of_month', 
#	DAYOFYEAR( DATE_ADD( if( cphd.harv_end is null, cphda.harv_end, cphd.harv_end ), INTERVAL 1 DAY ) ) as 'day_of_year', 
#	'no burning' as 'burn_type' 
#FROM 
#	comet.crop_planting_harvest_dates cphd 
#	LEFT JOIN car2017.crop_planting_harvest_dates_averages cphda ON cphd.cdl_name = cphda.cdl_name 
#	LEFT JOIN car2017.cropland_crops pc ON cphd.statecode = pc.statecode AND cphd.cdl_name = pc.cropname1 
#WHERE 
#	pc.cropname1 IN ( 'grass', 'grass_legume mix', 'grass-legume mix', 'grass_clover mix', 'grass_hay', 'alfalfa', 'switchgrass', 'clover', 'grass_pasture' );

# *************************************************************************************************************
# ******************** Set the future management attributes for the conservation practices ********************
# *************************************************************************************************************

# ********************************************************** 
# ********* Intensive Tillage to No Tillage or Strip Tillage
# ********************************************************** 
SET @practice = 'Intensive Tillage to No Tillage or Strip Tillage';
CALL changeTillage( @practice, 'Intensive Tillage', 'No Tillage', 'future' );

# ********************************************************** 
# ********* Intensive Tillage to Reduced Tillage
# ********************************************************** 
SET @practice = 'Intensive Tillage to Reduced Tillage';
CALL changeTillage( @practice, 'Intensive Tillage', 'Reduced Tillage', 'future' );

# ********************************************************** 
# ********* Intensive Tillage to Mulch Tillage
# ********************************************************** 
SET @practice = 'Intensive Tillage to Mulch Tillage';
CALL changeTillage( @practice, 'Intensive Tillage', 'Mulch Tillage', 'future' );

# ********************************************************** 
# ********* Intensive Tillage to Ridge Tillage
# ********************************************************** 
SET @practice = 'Intensive Tillage to Ridge Tillage';
CALL changeTillage( @practice, 'Intensive Tillage', 'Ridge Tillage', 'future' );

# ********************************************************** 
# ********* Reduced Tillage to No Tillage
# ********************************************************** 
SET @practice = 'Reduced Tillage to No Tillage';
CALL changeTillage( @practice, 'Intensive Tillage', 'Reduced Tillage', 'current' );
CALL changeTillage( @practice, 'Intensive Tillage', 'No Tillage', 'future' );

# ********************************************************** 
# ********* Reduced Tillage to Ridge Tillage
# ********************************************************** 
SET @practice = 'Reduced Tillage to Ridge Tillage';

CALL changeTillage( @practice, 'Intensive Tillage', 'Reduced Tillage', 'current' );
CALL changeTillage( @practice, 'Intensive Tillage', 'Ridge Tillage', 'future' );

# ********************************************************** 
# ********* Reduced Tillage to Mulch Tillage
# ********************************************************** 
SET @practice = 'Reduced Tillage to Mulch Tillage';

CALL changeTillage( @practice, 'Intensive Tillage', 'Reduced Tillage', 'current' );
CALL changeTillage( @practice, 'Intensive Tillage', 'Mulch Tillage', 'future' );

# ********************************************************** 
# ********* Nutrient Management - Improved Nitrogen Fertilizer Management - Use of Slow Release Fertilizers
# ********************************************************** 
SET @practice = 'Nutrient Management - Improved Nitrogen Fertilizer Management - Use of Slow Release Fertilizers';

CALL changeNfertEEP( @practice, 'Slow Release', 'future' );

# ********************************************************** 
# ********* Nutrient Management - Improved Nitrogen Fertilizer Management - Use of Nitrification Inhibitors
# ********************************************************** 
SET @practice = 'Nutrient Management - Improved Nitrogen Fertilizer Management - Use of Nitrification Inhibitors';

CALL changeNfertEEP( @practice, 'Nitrification Inhibitor', 'future' );

# ********************************************************** 
# ********* Nutrient Management - Improved Nitrogen Fertilizer Management - Fertilizer Reductions
# ********************************************************** 
SET @practice = 'Nutrient Management - Improved Nitrogen Fertilizer Management - Fertilizer Reductions';
SET @omad_n_fraction = 0.0;
SET @covercrop_n_fraction = 0.0;
SET @nfert_eep = 'None';
SET @nfert_reduction_fraction = 0.85;

CALL changeNfert( @practice, @omad_n_fraction, @covercrop_n_fraction, @nfert_reduction_fraction, @nfert_eep );

# ********************************************************** 
# ********* Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments
# ********************************************************** 
#   1) Add in an OMAD record equivalent to NFERT N amount
#   Options are:  
#	OMAD type			% N	CN ratio
#	- Farmyard Manure		2.5	12
#	- Compost (CN 18)		2	18
#	- Compost (CN 10)		3.6	10
#	- Compost (CN 15)		2.4	15
#	- Compost (CN 20)		1.8	20
#	- Compost (CN 25)		1.4	25
#	- Other				2.5	12
#	- Beef				2.3	12
#	- Chicken - Layer		4.5	8
#	- Dairy				2.1	12
#	- Chicken - Broiler (litter)	4.3	8
#	- Sheep				2.3	12
#	- Swine				3.3	15

# ********************************************************** 
# ********* Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 10)
# ********************************************************** 
SET @practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 10)';
SET @omad_type = 'Compost or Composted Manure';
SET @omad_n_pct = 3.6;
SET @omad_cn_ratio = 10;
SET @omad_n_fraction = 0.00; # reset from 1.0, N reductions handled in the python script
SET @covercrop_n_fraction = 0.00;

# Reduce nfert
CALL changeNfert( @practice, @omad_n_fraction, @covercrop_n_fraction, 1.0, "None" );

#Add OMAD
CALL addOMAD( @practice, @omad_n_fraction, @omad_n_pct, @omad_cn_ratio, @omad_type );

# ********************************************************** 
# ********* Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 15)
# ********************************************************** 
SET @practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 15)';
SET @omad_type = 'Compost or Composted Manure';
SET @omad_n_pct = 2.4;
SET @omad_cn_ratio = 15;
SET @omad_n_fraction = 0.00; # reset from 1.0, N reductions handled in the python script
SET @covercrop_n_fraction = 0.00;

# Reduce nfert
CALL changeNfert( @practice, @omad_n_fraction, @covercrop_n_fraction, 1.0, "None" );

# Add OMAD
CALL addOMAD( @practice, @omad_n_fraction, @omad_n_pct, @omad_cn_ratio, @omad_type );

# ********************************************************** 
# ********* Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 20)
# ********************************************************** 
SET @practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 20)';
SET @omad_type = 'Compost or Composted Manure';
SET @omad_n_pct = 1.8;
SET @omad_cn_ratio = 20;
SET @omad_n_fraction = 0.00; # reset from 1.0, N reductions handled in the python script
SET @covercrop_n_fraction = 0.00;

# Reduce nfert
CALL changeNfert( @practice, @omad_n_fraction, @covercrop_n_fraction, 1.0, "None" );

# Add OMAD
CALL addOMAD( @practice, @omad_n_fraction, @omad_n_pct, @omad_cn_ratio, @omad_type );

# ********************************************************** 
# ********* Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 25)
# ********************************************************** 
SET @practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 25)';
SET @omad_type = 'Compost or Composted Manure';
SET @omad_n_pct = 1.4;
SET @omad_cn_ratio = 25;
SET @omad_n_fraction = 0.00; # reset from 1.0, N reductions handled in the python script
SET @covercrop_n_fraction = 0.00;

# Reduce nfert
CALL changeNfert( @practice, @omad_n_fraction, @covercrop_n_fraction, 1.0, "None" );

# Add OMAD
CALL addOMAD( @practice, @omad_n_fraction, @omad_n_pct, @omad_cn_ratio, @omad_type );

# ********************************************************** 
# ********* Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Dairy Manure
# ********************************************************** 
SET @practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Dairy Manure';
SET @omad_type = 'Dairy';
SET @omad_n_pct = 2.1;
SET @omad_cn_ratio = 12;
SET @omad_n_fraction = 0.00; # reset from 0.50, N reductions handled in the python script
SET @covercrop_n_fraction = 0.00;

# Reduce nfert
CALL changeNfert( @practice, @omad_n_fraction, @covercrop_n_fraction, 1.0, "None" );

# Add OMAD
CALL addOMAD( @practice, @omad_n_fraction, @omad_n_pct, @omad_cn_ratio, @omad_type );

# ********************************************************** 
# ********* Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Beef Feedlot Manure
# ********************************************************** 
SET @practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Beef Feedlot Manure';
SET @omad_type = 'Beef';
SET @omad_n_pct = 2.3;
SET @omad_cn_ratio = 12;
SET @omad_n_fraction = 0.00; # reset from 0.50, N reductions handled in the python script
SET @covercrop_n_fraction = 0.00;

# Reduce nfert
CALL changeNfert( @practice, @omad_n_fraction, @covercrop_n_fraction, 1.0, "None" );

# Add OMAD
CALL addOMAD( @practice, @omad_n_fraction, @omad_n_pct, @omad_cn_ratio, @omad_type );

# ********************************************************** 
# ********* Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Other Manure
# ********************************************************** 
SET @practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Other Manure';
SET @omad_type = 'Other';
SET @omad_n_pct = 2.5;
SET @omad_cn_ratio = 12;
SET @omad_n_fraction = 0.00; # reset from 0.50, N reductions handled in the python script
SET @covercrop_n_fraction = 0.00;

# Reduce nfert
CALL changeNfert( @practice, @omad_n_fraction, @covercrop_n_fraction, 1.0, "None" );

# Add OMAD
CALL addOMAD( @practice, @omad_n_fraction, @omad_n_pct, @omad_cn_ratio, @omad_type );

# ********************************************************** 
# ********* Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Chicken Layer Manure 
# ********************************************************** 
SET @practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Chicken Layer Manure';
SET @omad_type = 'Chicken - Layer';
SET @omad_n_pct = 4.5;
SET @omad_cn_ratio = 8;
SET @omad_n_fraction = 0.00; # reset from 0.50, N reductions handled in the python script
SET @covercrop_n_fraction = 0.00;

# Reduce nfert
CALL changeNfert( @practice, @omad_n_fraction, @covercrop_n_fraction, 1.0, "None" );

# Add OMAD
CALL addOMAD( @practice, @omad_n_fraction, @omad_n_pct, @omad_cn_ratio, @omad_type );

# ********************************************************** 
# ********* Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Chicken Broiler Manure
# ********************************************************** 
SET @practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Chicken Broiler Manure';
SET @omad_type = 'Chicken - Broiler (Litter)';
SET @omad_n_pct = 4.3;
SET @omad_cn_ratio = 8;
SET @omad_n_fraction = 0.00; # reset from 0.50, N reductions handled in the python script
SET @covercrop_n_fraction = 0.00;

# Reduce nfert
CALL changeNfert( @practice, @omad_n_fraction, @covercrop_n_fraction, 1.0, "None" );

# Add OMAD
CALL addOMAD( @practice, @omad_n_fraction, @omad_n_pct, @omad_cn_ratio, @omad_type );

# ********************************************************** 
# ********* Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Sheep Manure
# ********************************************************** 
SET @practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Sheep Manure';
SET @omad_type = 'Sheep';
SET @omad_n_pct = 2.3;
SET @omad_cn_ratio = 12;
SET @omad_n_fraction = 0.00; # reset from 0.50, N reductions handled in the python script
SET @covercrop_n_fraction = 0.00;

# Reduce nfert
CALL changeNfert( @practice, @omad_n_fraction, @covercrop_n_fraction, 1.0, "None" );

# Add OMAD
CALL addOMAD( @practice, @omad_n_fraction, @omad_n_pct, @omad_cn_ratio, @omad_type );

# ********************************************************** 
# ********* Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Swine Manure
# ********************************************************** 
SET @practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Swine Manure';
SET @omad_type = 'Swine';
SET @omad_n_pct = 3.3;
SET @omad_cn_ratio = 15;
SET @omad_n_fraction = 0.00; # reset from 0.50, N reductions handled in the python script
SET @covercrop_n_fraction = 0.00;

# Reduce nfert
CALL changeNfert( @practice, @omad_n_fraction, @covercrop_n_fraction, 1.0, "None" );

# Add OMAD
CALL addOMAD( @practice, @omad_n_fraction, @omad_n_pct, @omad_cn_ratio, @omad_type );

# ********************************************************** 
# ********* Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Green manure/cover crops
# ********************************************************** 
#Per conversation with Amy on 12/8/2016, removing green manure/cover crops as it is redundant
#SET @practice = 'Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Green manure/cover crops';
#   Replaces 50% of synthetic fertilizer with leguminous cover crop
#   Update the nfert value to 50% of typical fertilizer rates
#1st and 2nd crop in sequence are treated the same.
#SET @omad_n_fraction = 0.0;
#SET @covercrop_n_fraction = 0.25;

# Reduce nfert
#CALL changeNfert( @practice, @omad_n_fraction, @covercrop_n_fraction, 1.0, "None" );

# ********************************************************** 
# ********* Cover Crops - Leguminous
# ********************************************************** 
#SET @practice = 'Cover Crops - Leguminous';
# These were previously set in the previous bulk update statements for cover crops

# reduce Nfert
SET @omad_n_fraction = 0.0;
SET @covercrop_n_fraction = 0.50;

CALL changeNfert( @practice, @omad_n_fraction, @covercrop_n_fraction, 1.0, "None" );

# ********************************************************** 
# ********* Cover Crops - Non-leguminous
# ********************************************************** 
#SET @practice = 'Cover Crops - Non-leguminous';
# These were previously set in the previous bulk update statements for cover crops

SET @omad_n_fraction = 0.0;
SET @covercrop_n_fraction = 0.25;

CALL changeNfert( @practice, @omad_n_fraction, @covercrop_n_fraction, 1.0, "None" );

# ********************************************************** 
# ********* Intensive Tillage to No Tillage or Strip Tillage + Nutrient Management - Improved Nitrogen Fertilizer Management - Fertilizer Reductions
# ********************************************************** 
SET @practice = 'Intensive Tillage to No Tillage or Strip Tillage + Nutrient Management - Improved Nitrogen Fertilizer Management - Fertilizer Reductions';
SET @omad_n_fraction = 0.0;
SET @covercrop_n_fraction = 0.0;
SET @nfert_reduction_fraction = 0.85;

#   Update the tillage type
CALL changeTillage( @practice, 'Intensive Tillage', 'No Tillage', 'future' );

#   Reduce fertilizer amount by 15%
CALL changeNfert( @practice, @omad_n_fraction, @covercrop_n_fraction, @nfert_reduction_fraction, "None" );

# ********************************************************** 
# ********* Intensive Tillage to No Tillage or Strip Tillage + non-Leguminous Cover Crops
# ********************************************************** 
SET @practice = 'Intensive Tillage to No Tillage or Strip Tillage + non-Leguminous Cover Crops';

#   Update the tillage type
CALL changeTillage( @practice, 'Intensive Tillage', 'No Tillage', 'future' );

# reduce Nfert
SET @omad_n_fraction = 0.0;
SET @covercrop_n_fraction = 0.25;
CALL changeNfert( @practice, @omad_n_fraction, @covercrop_n_fraction, 1.0, "None" );

# ********************************************************** 
# ********* Intensive Tillage to No Tillage or Strip Tillage + non-Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 10)
# ********************************************************** 
SET @practice = 'Intensive Tillage to No Tillage or Strip Tillage + non-Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 10)';
SET @omad_type = 'Compost or Composted Manure';
SET @omad_n_pct = 3.6;
SET @omad_cn_ratio = 10;
SET @omad_n_fraction = 0.00; # reset from 0.75, N reductions handled in the python script
SET @covercrop_n_fraction = 0.25;

#  Update the tillage
CALL changeTillage( @practice, 'Intensive Tillage', 'No Tillage', 'future' );

# Reduce nfert
CALL changeNfert( @practice, @omad_n_fraction, @covercrop_n_fraction, 1.0, "None" );

# Add OMAD
CALL addOMAD( @practice, @omad_n_fraction, @omad_n_pct, @omad_cn_ratio, @omad_type );

# ********************************************************** 
# ********* Intensive Tillage to No Tillage or Strip Tillage + non-Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 15)
# ********************************************************** 
SET @practice = 'Intensive Tillage to No Tillage or Strip Tillage + non-Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 15)';
SET @omad_type = 'Compost or Composted Manure';
SET @omad_n_pct = 2.4;
SET @omad_cn_ratio = 15;
SET @omad_n_fraction = 0.00; # reset from 0.75, N reductions handled in the python script
SET @covercrop_n_fraction = 0.25;

#  Update the tillage
CALL changeTillage( @practice, 'Intensive Tillage', 'No Tillage', 'future' );

# Reduce nfert
CALL changeNfert( @practice, @omad_n_fraction, @covercrop_n_fraction, 1.0, "None" );

# Add OMAD
CALL addOMAD( @practice, @omad_n_fraction, @omad_n_pct, @omad_cn_ratio, @omad_type );

# ********************************************************** 
# ********* Intensive Tillage to No Tillage or Strip Tillage + non-Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 20)
# ********************************************************** 
SET @practice = 'Intensive Tillage to No Tillage or Strip Tillage + non-Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 20)';
SET @omad_type = 'Compost or Composted Manure';
SET @omad_n_pct = 1.8;
SET @omad_cn_ratio = 20;
SET @omad_n_fraction = 0.00; # reset from 0.75, N reductions handled in the python script
SET @covercrop_n_fraction = 0.25;

#  Update the tillage
CALL changeTillage( @practice, 'Intensive Tillage', 'No Tillage', 'future' );

# Reduce nfert
CALL changeNfert( @practice, @omad_n_fraction, @covercrop_n_fraction, 1.0, "None" );

# Add OMAD
CALL addOMAD( @practice, @omad_n_fraction, @omad_n_pct, @omad_cn_ratio, @omad_type );

# ********************************************************** 
# ********* Intensive Tillage to No Tillage or Strip Tillage + non-Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 25)
# ********************************************************** 
SET @practice = 'Intensive Tillage to No Tillage or Strip Tillage + non-Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 25)';
SET @omad_type = 'Compost or Composted Manure';
SET @omad_n_pct = 1.4;
SET @omad_cn_ratio = 25;
SET @omad_n_fraction = 0.00; # reset from 0.75, N reductions handled in the python script
SET @covercrop_n_fraction = 0.25;

#  Update the tillage
CALL changeTillage( @practice, 'Intensive Tillage', 'No Tillage', 'future' );

# Reduce nfert
CALL changeNfert( @practice, @omad_n_fraction, @covercrop_n_fraction, 1.0, "None" );

# Add OMAD
CALL addOMAD( @practice, @omad_n_fraction, @omad_n_pct, @omad_cn_ratio, @omad_type );

# ********************************************************** 
# *********** Intensive Tillage to No Tillage or Strip Tillage + Leguminous Cover Crops
# ********************************************************** 
SET @practice = 'Intensive Tillage to No Tillage or Strip Tillage + Leguminous Cover Crops';
SET @omad_n_fraction = 0.0;
SET @covercrop_n_fraction = 0.50;

#   Change tillage to No Tillage
CALL changeTillage( @practice, 'Intensive Tillage', 'No Tillage', 'future' );

# Reduce nfert
CALL changeNfert( @practice, @omad_n_fraction, @covercrop_n_fraction, 1.0, "None" );

# ********************************************************** 
# ********* Intensive Tillage to No Tillage or Strip Tillage + Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 10)
# ********************************************************** 
SET @practice = 'Intensive Tillage to No Tillage or Strip Tillage + Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 10)';
SET @omad_type = 'Compost or Composted Manure';
SET @omad_n_pct = 3.6;
SET @omad_cn_ratio = 10;
SET @omad_n_fraction = 0.00; # reset from 0.50, N reductions handled in the python script
SET @covercrop_n_fraction = 0.50;

# Set tillage to 'no tillage'
CALL changeTillage( @practice, 'Intensive Tillage', 'No Tillage', 'future' );

# Reduce nfert
CALL changeNfert( @practice, @omad_n_fraction, @covercrop_n_fraction, 1.0, "None" );

# Add OMAD
CALL addOMAD( @practice, @omad_n_fraction, @omad_n_pct, @omad_cn_ratio, @omad_type );

# ********************************************************** 
# ********* Intensive Tillage to No Tillage or Strip Tillage + Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 15)
# ********************************************************** 
SET @practice = 'Intensive Tillage to No Tillage or Strip Tillage + Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 15)';
SET @omad_type = 'Compost or Composted Manure';
SET @omad_n_pct = 2.4;
SET @omad_cn_ratio = 15;
SET @omad_n_fraction = 0.00; # reset from 0.50, N reductions handled in the python script
SET @covercrop_n_fraction = 0.50;

# Set tillage to 'no tillage'
CALL changeTillage( @practice, 'Intensive Tillage', 'No Tillage', 'future' );

#  Reduce nfert
CALL changeNfert( @practice, @omad_n_fraction, @covercrop_n_fraction, 1.0, "None" );

# Add OMAD
CALL addOMAD( @practice, @omad_n_fraction, @omad_n_pct, @omad_cn_ratio, @omad_type );

# ********************************************************** 
# ********* Intensive Tillage to No Tillage or Strip Tillage + Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 20)
# ********************************************************** 
SET @practice = 'Intensive Tillage to No Tillage or Strip Tillage + Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 20)';
SET @omad_type = 'Compost or Composted Manure';
SET @omad_n_pct = 1.8;
SET @omad_cn_ratio = 20;
SET @omad_n_fraction = 0.00; # reset from 0.50, N reductions handled in the python script
SET @covercrop_n_fraction = 0.50;

# Set tillage to 'no tillage'
CALL changeTillage( @practice, 'Intensive Tillage', 'No Tillage', 'future' );

# Reduce nfert
CALL changeNfert( @practice, @omad_n_fraction, @covercrop_n_fraction, 1.0, "None" );

# Add OMAD
CALL addOMAD( @practice, @omad_n_fraction, @omad_n_pct, @omad_cn_ratio, @omad_type );

# ********************************************************** 
# ********* Intensive Tillage to No Tillage or Strip Tillage + Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 25)
# ********************************************************** 
SET @practice = 'Intensive Tillage to No Tillage or Strip Tillage + Leguminous Cover Crops + Nutrient Management - Replacement of Synthetic Nitrogen Fertilizer with Soil Amendments - Compost (CN 25)';
SET @omad_type = 'Compost or Composted Manure';
SET @omad_n_pct = 1.4;
SET @omad_cn_ratio = 25;
SET @omad_n_fraction = 0.00; # reset from 0.50, N reductions handled in the python script
SET @covercrop_n_fraction = 0.50;

# Set tillage to 'no tillage'
CALL changeTillage( @practice, 'Intensive Tillage', 'No Tillage', 'future' );

# Reduce nfert
CALL changeNfert( @practice, @omad_n_fraction, @covercrop_n_fraction, 1.0, "None" );

# Add OMAD
CALL addOMAD( @practice, @omad_n_fraction, @omad_n_pct, @omad_cn_ratio, @omad_type );

# ********************************************************** 
# ********* Conversion to non-legume grassland reserve
# ********************************************************** 
SET @practice = 'Conversion to non-legume grassland reserve';

#change crop to grass
UPDATE 
	comet.planner_cropland_crops pc 
	JOIN comet.planner_cropland_cps_list pcl ON pc.id_planner_cropland_cps_list = pcl.id 
SET 
	cdl_name = 'grass_hay',
	cropname1 = 'grass_hay',
	cfarm_cropname1 = 'Grass', 
	pltm_or_frst1 = 'frst' 
WHERE 
	pcl.practice = @practice 
	AND current_or_future = 'future';

#delete harvest events
DELETE FROM comet.planner_cropland_harvests 
WHERE 
	id_planner_cropland_crops IN ( SELECT id FROM comet.planner_cropland_crops WHERE current_or_future = 'future' AND id_planner_cropland_cps_list IN (SELECT id FROM comet.planner_cropland_cps_list WHERE practice = @practice ) );

#delete irrigation events
DELETE FROM comet.planner_cropland_irrig 
WHERE 
	id_planner_cropland_crops IN ( SELECT id FROM comet.planner_cropland_crops WHERE current_or_future = 'future' AND id_planner_cropland_cps_list IN (SELECT id FROM comet.planner_cropland_cps_list WHERE practice = @practice ) );

#delete N fertilization events
DELETE FROM comet.planner_cropland_nfert 
WHERE 
	id_planner_cropland_crops IN ( SELECT id FROM comet.planner_cropland_crops WHERE current_or_future = 'future' AND id_planner_cropland_cps_list IN (SELECT id FROM comet.planner_cropland_cps_list WHERE practice = @practice ) );

#delete tillage events
DELETE FROM comet.planner_cropland_tillage 
WHERE 
	id_planner_cropland_crops IN ( SELECT id FROM comet.planner_cropland_crops WHERE current_or_future = 'future' AND id_planner_cropland_cps_list IN (SELECT id FROM comet.planner_cropland_cps_list WHERE practice = @practice ) );


# ********************************************************** 
# ********* Conversion to grass-legume grassland reserve
# ********************************************************** 
SET @practice = 'Conversion to grass-legume grassland reserve';

#change crop to grass
UPDATE 
	comet.planner_cropland_crops pc 
	JOIN comet.planner_cropland_cps_list pcl ON pc.id_planner_cropland_cps_list = pcl.id 
SET 
	cdl_name = 'grass_hay',
	cropname1 = 'grass_hay',
	cfarm_cropname1 = 'Grass-Legume Mix',
	pltm_or_frst1 = 'frst' 
WHERE 
	pcl.practice = @practice 
	AND current_or_future = 'future';

#delete harvest events
DELETE FROM comet.planner_cropland_harvests 
WHERE 
	id_planner_cropland_crops IN ( SELECT id FROM comet.planner_cropland_crops WHERE current_or_future = 'future' AND id_planner_cropland_cps_list IN (SELECT id FROM comet.planner_cropland_cps_list WHERE practice = @practice ) );

#delete irrigation events
DELETE FROM comet.planner_cropland_irrig 
WHERE 
	id_planner_cropland_crops IN ( SELECT id FROM comet.planner_cropland_crops WHERE current_or_future = 'future' AND id_planner_cropland_cps_list IN (SELECT id FROM comet.planner_cropland_cps_list WHERE practice = @practice ) );

#delete N fertilization events
DELETE FROM comet.planner_cropland_nfert 
WHERE 
	id_planner_cropland_crops IN ( SELECT id FROM comet.planner_cropland_crops WHERE current_or_future = 'future' AND id_planner_cropland_cps_list IN (SELECT id FROM comet.planner_cropland_cps_list WHERE practice = @practice ) );

#delete tillage events
DELETE FROM comet.planner_cropland_tillage 
WHERE 
	id_planner_cropland_crops IN ( SELECT id FROM comet.planner_cropland_crops WHERE current_or_future = 'future' AND id_planner_cropland_cps_list IN (SELECT id FROM comet.planner_cropland_cps_list WHERE practice = @practice ) );

# ********************************************************** 
# ********* Conversion to grass-legume forage production
# ********************************************************** 
SET @practice = 'Conversion to grass-legume forage production';

#change crop to grass-legume
UPDATE 
	comet.planner_cropland_crops pc 
	JOIN comet.planner_cropland_cps_list pcl ON pc.id_planner_cropland_cps_list = pcl.id 
SET 
	cdl_name = 'grass_hay',
	cropname1 = 'grass_hay',
	cfarm_cropname1 = 'Grass-Legume Mix',
	pltm_or_frst1 = 'frst', 
	plant_month1 = 1, 
	plant_dayofmonth1 = 3, 
	plant_dayofyear1 = 3 
WHERE 
	pcl.practice = @practice 
	AND current_or_future = 'future';

#delete existing harvest events
DELETE FROM comet.planner_cropland_harvests 
WHERE 
	id_planner_cropland_crops IN ( SELECT id FROM comet.planner_cropland_crops WHERE current_or_future = 'future' AND id_planner_cropland_cps_list IN (SELECT id FROM comet.planner_cropland_cps_list WHERE practice = @practice ) );

#delete existing irrigation events
DELETE FROM comet.planner_cropland_irrig 
WHERE 
	id_planner_cropland_crops IN ( SELECT id FROM comet.planner_cropland_crops WHERE current_or_future = 'future' AND id_planner_cropland_cps_list IN (SELECT id FROM comet.planner_cropland_cps_list WHERE practice = @practice ) );

#delete existing N fertilization events
DELETE FROM comet.planner_cropland_nfert 
WHERE 
	id_planner_cropland_crops IN ( SELECT id FROM comet.planner_cropland_crops WHERE current_or_future = 'future' AND id_planner_cropland_cps_list IN (SELECT id FROM comet.planner_cropland_cps_list WHERE practice = @practice ) );

#delete existing tillage events
DELETE FROM comet.planner_cropland_tillage 
WHERE 
	id_planner_cropland_crops IN ( SELECT id FROM comet.planner_cropland_crops WHERE current_or_future = 'future' AND id_planner_cropland_cps_list IN (SELECT id FROM comet.planner_cropland_cps_list WHERE practice = @practice ) );

# Add back the Hay Harvests
# Add a harvest on the 1st day of harvest season, and for up to six additional harvests after that
DROP PROCEDURE IF EXISTS addHayHarvestsToForageProduction;
DELIMITER //
CREATE PROCEDURE addHayHarvestsToForageProduction()
BEGIN
	DECLARE x INT;
	SET x = 0;
	WHILE x < 7 DO
		INSERT INTO comet.planner_cropland_harvests ( id_planner_cropland_crops, number_of_harvests, month, day_of_month, day_of_year, grain, yield, strawstoverhayremoval ) 
		SELECT DISTINCT pc.id as 'id_planner_cropland_crops', ( DAYOFYEAR( cphd.harv_end ) - DAYOFYEAR( cphd.harv_start ) ) / 45 AS 'number_of_harvests', MONTH( ADDDATE( cphd.harv_start, 45 * x ) ) as 'month', DAYOFMONTH( ADDDATE( cphd.harv_start, 45 * x ) ) as 'day_of_month', DAYOFYEAR( ADDDATE( cphd.harv_start, 45 * x ) ) as 'day_of_year', 'No' AS 'grain', ROUND( AVG( IF( nrd.value IS NULL, nrda.value, nrd.value ) ), IF( CAST( AVG( nrda.value ) AS INTEGER ) < 20, 1, 0 ) ) AS 'yield', 50 AS 'strawstoverhayremoval' 
		FROM comet.crop_planting_harvest_dates cphd 
		LEFT JOIN comet.planner_cropland_crops pc ON cphd.statecode = pc.statecode AND cphd.cdl_name = pc.cropname1 
		LEFT JOIN comet.nass_raw_data nrd ON cphd.statecode = nrd.statecode AND cphd.nass_name = nrd.cropname 
		LEFT JOIN comet.nass_raw_data_averages nrda ON cphd.nass_name = nrda.cropname 
		LEFT JOIN comet.planner_cropland_cps_list pcl ON pc.id_planner_cropland_cps_list = pcl.id 
		WHERE pcl.practice = @practice AND current_or_future = 'future' AND ( DAYOFYEAR( cphd.harv_end ) - DAYOFYEAR( cphd.harv_start ) ) / 45 > x GROUP BY pc.id, ( DAYOFYEAR( cphd.harv_end ) - DAYOFYEAR( cphd.harv_start ) ) / 45, DAYOFYEAR( ADDDATE( cphd.harv_start, 45 * x ) );
		SET x = x + 1;
	END WHILE;
	#Add a final harvest on the last day of harvest season
	INSERT INTO comet.planner_cropland_harvests ( id_planner_cropland_crops, number_of_harvests, month, day_of_month, day_of_year, grain, yield, strawstoverhayremoval ) 
	SELECT DISTINCT pc.id as 'id_planner_cropland_crops', ( DAYOFYEAR( cphd.harv_end ) - DAYOFYEAR( cphd.harv_start ) ) / 45 AS 'number_of_harvests', MONTH( ADDDATE( cphd.harv_start, 45 * x ) ) as 'month', DAYOFMONTH( ADDDATE( cphd.harv_start, 45 * x ) ) as 'day_of_month', DAYOFYEAR( cphd.harv_end ) as 'day_of_year', 'No' AS 'grain', 
	ROUND( AVG( IF( nrd.value IS NULL, nrda.value, nrd.value ) ), IF( CAST( AVG( IF( nrd.value IS NULL, nrda.value, nrd.value ) ) AS INTEGER ) < 10, 1, 0 ) ) AS 'yield', 
	50 AS 'strawstoverhayremoval' 
	FROM comet.crop_planting_harvest_dates cphd 
	LEFT JOIN comet.planner_cropland_crops pc ON cphd.statecode = pc.statecode AND cphd.cdl_name = pc.cropname1 
	LEFT JOIN comet.nass_raw_data nrd ON cphd.statecode = nrd.statecode AND cphd.nass_name = nrd.cropname 
	LEFT JOIN comet.nass_raw_data_averages nrda ON cphd.nass_name = nrda.cropname 
	LEFT JOIN comet.planner_cropland_cps_list pcl ON pc.id_planner_cropland_cps_list = pcl.id 
	WHERE pcl.practice = @practice AND current_or_future = 'future' AND pc.cropname1 IN ( 'grass_legume mix', 'grass_clover mix', 'grass_hay', 'alfalfa' ) 
	GROUP BY pc.id, ( DAYOFYEAR( cphd.harv_end ) - DAYOFYEAR( cphd.harv_start ) ) / 45, DAYOFYEAR( cphd.harv_end );
END //
DELIMITER ;

CALL addHayHarvestsToForageProduction();

# Add back the Irrigation Events
DROP PROCEDURE IF EXISTS addHayIrrigationToForageProduction;
DELIMITER //
CREATE PROCEDURE addHayIrrigationToForageProduction()
BEGIN
	DECLARE x INT;
	SET x = 0;
	WHILE x < 53 DO
		INSERT INTO comet.planner_cropland_irrig ( id_planner_cropland_crops, number_of_irrig_events, month, day_of_month, day_of_year, irrig_amount ) SELECT DISTINCT pc.id as 'id_planner_cropland_crops', ( DAYOFYEAR( cphd.harv_end ) - DAYOFYEAR( cphd.harv_start ) ) / 7 AS 'number_of_irrig_events', MONTH( DATE_ADD( cphd.harv_start, INTERVAL ( x * 7 ) DAY ) ) AS 'month', DAYOFMONTH( DATE_ADD( cphd.harv_start, INTERVAL ( x * 7 ) DAY ) ) AS 'day_of_month', DAYOFYEAR( DATE_ADD( cphd.harv_start, INTERVAL ( x * 7 ) DAY ) ) as 'day_of_year', 2.54 as 'irrig_amount' 
		FROM comet.crop_planting_harvest_dates cphd 
		JOIN comet.planner_cropland_crops pc ON cphd.statecode = pc.statecode AND cphd.cdl_name = pc.cropname1 
		JOIN comet.planner_cropland_cps_list pcl ON pc.id_planner_cropland_cps_list = pcl.id 
		WHERE pcl.practice = @practice AND current_or_future = 'future' AND pc.cropname1 IN ( 'grass_legume mix', 'grass_clover mix', 'grass_hay', 'alfalfa', 'grass_pasture' ) AND pc.irrigated1 = 'Y' AND ( DAYOFYEAR( cphd.harv_end ) - DAYOFYEAR( cphd.harv_start ) ) / 7 > x;
		SET x = x + 1;
	END WHILE;
END //
DELIMITER ;

CALL addHayIrrigationToForageProduction();

# Order and index the tables for subsequent fast processing when building the input .xml files:
alter table comet.planner_cropland_burning drop column id;
alter table comet.planner_cropland_burning order by id_planner_cropland_crops, day_of_year;
alter table comet.planner_cropland_burning add column id integer auto_increment primary key;
alter table comet.planner_cropland_burning add index( id_planner_cropland_crops, day_of_year );

alter table comet.planner_cropland_grazing drop column id;
alter table comet.planner_cropland_grazing order by id_planner_cropland_crops, start_day_of_year;
alter table comet.planner_cropland_grazing add column id integer auto_increment primary key;
alter table comet.planner_cropland_grazing add index( id_planner_cropland_crops, start_day_of_year );

alter table comet.planner_cropland_irrig drop column id;
alter table comet.planner_cropland_irrig order by id_planner_cropland_crops, day_of_year;
alter table comet.planner_cropland_irrig add column id integer auto_increment primary key;
alter table comet.planner_cropland_irrig add index( id_planner_cropland_crops, day_of_year );

alter table comet.planner_cropland_tillage drop column id;
alter table comet.planner_cropland_tillage order by id_planner_cropland_crops, day_of_year;
alter table comet.planner_cropland_tillage add column id integer auto_increment primary key;
alter table comet.planner_cropland_tillage add index( id_planner_cropland_crops, day_of_year );

alter table comet.planner_cropland_nfert drop column id;
alter table comet.planner_cropland_nfert order by id_planner_cropland_crops, day_of_year;
alter table comet.planner_cropland_nfert add column id integer auto_increment primary key;
alter table comet.planner_cropland_nfert add index( id_planner_cropland_crops, day_of_year );

alter table comet.planner_cropland_harvests drop column id;
alter table comet.planner_cropland_harvests order by id_planner_cropland_crops, day_of_year;
alter table comet.planner_cropland_harvests add column id integer auto_increment primary key;
alter table comet.planner_cropland_harvests add index( id_planner_cropland_crops, day_of_year );

alter table comet.planner_cropland_omad drop column id;
alter table comet.planner_cropland_omad order by id_planner_cropland_crops, day_of_year;
alter table comet.planner_cropland_omad add column id integer auto_increment primary key;
alter table comet.planner_cropland_omad add index( id_planner_cropland_crops, day_of_year );
