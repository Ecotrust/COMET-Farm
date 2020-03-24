# This script generates the input files necessary to hold the DayCent model results generated by the COMET-Farm API
# It is used with a MariaDB (MySQL) database

DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_aagdefac; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_aagdefac ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_abgdefac; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_abgdefac ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_accrst; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_accrst ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_accrste_1_; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_accrste_1_ ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_agcprd; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_agcprd ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_aglivc; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_aglivc ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_annppt; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_annppt ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_bgdefac; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_bgdefac ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_bglivcm; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_bglivcm ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_cgrain; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_cgrain ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_cinput; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_cinput ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_crmvst; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_crmvst ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_crootc; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_crootc ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_crpval; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_crpval ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_egracc_1_; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_egracc_1_ ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_eupacc_1_; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_eupacc_1_ ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_fbrchc; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_fbrchc ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_fertac_1_; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_fertac_1_ ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_fertac_1; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_fertac_1 ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_fertot_1_1_; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_fertot_1_1_ ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_frootcm; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_frootcm ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_gromin_1_; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_gromin_1_ ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_inputcrop; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_inputcrop ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_irrigated; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_irrigated ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_irrtot; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_irrtot ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_metabc_1_; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_metabc_1_ ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_metabc_2_; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_metabc_2_ ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_metabe_1_1_; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_metabe_1_1_ ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_metabe_2_1_; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_metabe_2_1_ ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_n2oflux; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_n2oflux ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_nfixac; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_nfixac ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_noflux; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_noflux ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_omadac; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_omadac ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_omadae_1_; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_omadae_1_ ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_petann; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_petann ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_rlwodc; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_rlwodc ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_somsc; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_somsc ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_somse_1_; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_somse_1_ ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_stdedc; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_stdedc ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_stdede_1_; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_stdede_1_ ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_strmac_1_; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_strmac_1_ ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_strmac_2_; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_strmac_2_ ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_strmac_6_; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_strmac_6_ ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_strucc_1_; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_strucc_1_ ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_struce_1_1_; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_struce_1_1_ ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_struce_2_1_; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_struce_2_1_ ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_tminrl_1_; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_tminrl_1_ ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_tnetmn_1_; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_tnetmn_1_ ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_volpac; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_volpac ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );
DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_year; CREATE TABLE cfarm_api_results.api_results_cropland_daycent_year ( id BIGINT AUTO_INCREMENT PRIMARY KEY, id_api_results_cropland_daycent_master BIGINT , date_value varchar( 8 ), output_value varchar( 20 ), INDEX( id_api_results_cropland_daycent_master, date_value ) );

DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland;
CREATE TABLE cfarm_api_results.api_results_cropland ( 
	id BIGINT AUTO_INCREMENT PRIMARY KEY, 
	name varchar(250), 
	id_mlra_crops_from_cdl_2009_2015 int(11), 
	id_mlra_grass_from_cdl_2009_2015 int(11), 
	mlra varchar(5), 
	practice varchar(200), 
	scenario varchar(200), 
	irrigated char(1), 
	soil_carbon_co2 float, 
	soil_carbon_co2_uncertainty float, 
	soil_carbon_stock_2000 float, 
	soil_carbon_stock_2000_uncertainty float, 
	soil_carbon_stock_begin float, 
	soil_carbon_stock_begin_uncertainty float, 
	soil_carbon_stock_end float, 
	soil_carbon_stock_end_uncertainty float, 
	soil_n2o float, 
	soil_n2o_uncertainty float, 
	biomass_burning_co2 float, 
	biomass_burning_co2_uncertainty float, 
	liming_co2 float, 
	liming_co2_uncertainty float, 
	ureafertilization_co2 float, 
	ureafertilization_co2_uncertainty float, 
	drainedorganicsoils_co2 float, 
	drainedorganicsoils_co2_uncertainty float, 
	biomassburning_co float, 
	biomassburning_co_uncertainty float, 
	wetlandricecultivation_n2o float, 
	wetlandricecultivation_n2o_uncertainty float, 
	biomassburning_n2o float, 
	biomassburning_n2o_uncertainty float, 
	drainedorganicsoils_n2o float, 
	drainedorganicsoils_n2o_uncertainty float, 
	soil_ch4 float, 
	soil_ch4_uncertainty float, 
	wetlandricecultivation_ch4 float, 
	wetlandricecultivation_ch4_uncertainty float, 
	biomassburning_ch4 float, 
	biomassburning_ch4_uncertainty float, 
	total_co2e float, 
	INDEX( id_mlra_crops_from_cdl_2009_2015 ), 
	INDEX( id_mlra_grass_from_cdl_2009_2015 ), 
	INDEX( practice, irrigated ), 
	INDEX( scenario ), 
	INDEX( mlra ) 
);

DROP TABLE IF EXISTS cfarm_api_results.api_results_cropland_daycent_master;
CREATE TABLE cfarm_api_results.api_results_cropland_daycent_master ( 
	id BIGINT AUTO_INCREMENT PRIMARY KEY, 
	name varchar(250), 
	id_mlra_crops_from_cdl_2009_2015 int(11), 
	mlra varchar(5), 
	practice varchar(200), 
	scenario varchar(200), 
	irrigated char(1), 
	mapunit int(11), 
	area float, 
	INDEX( id_mlra_crops_from_cdl_2009_2015 ), 
	INDEX( mlra, practice, scenario, irrigated )
);
