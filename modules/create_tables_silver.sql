-- CREATE TABLE 'materials' -- hist
CREATE TABLE materials_hist (
	-- Description product
	ID INT PRIMARY KEY,
	id_material VARCHAR ( 50 ) NOT NULL,   --id--
	name_material VARCHAR ( 50 ) NOT NULL,   --Título--
	label VARCHAR ( 50 ) NOT NULL,   --Etiquetas--
	parent VARCHAR ( 50 ) NOT NULL,   --parent--
	url VARCHAR ( 50 ) NOT NULL,   --url--
	-- Researcher and manufacturer
	realized_by VARCHAR ( 50 ),   --Realizado--
	manufacturer VARCHAR ( 50 ) NOT NULL,   --Fabricante--
	material_type VARCHAR ( 50 ) NOT NULL,   --Tipo--
	record_created_by VARCHAR ( 50 ) NOT NULL,   --created_by--
	record_last_edited_by VARCHAR ( 50 ) NOT NULL,   --last_edited_by--
	-- Date
	record_created_time TIMESTAMP  NOT NULL,   --created_time--
	record_last_edited_time TIMESTAMP  NOT NULL,   --last_edited_time--
	preparation_date VARCHAR ( 50 ) NOT NULL,   --Preparación--
	load_ts TIMESTAMP  NOT NULL,
	-- Percentage and ratio
	others_compounds VARCHAR ( 50 ),   --Otros compuestos--
	n_percentage FLOAT,   --%N--
	h_percentage FLOAT,   --%H--
	o_percentage FLOAT,   --%O--
	main_comp_percentage FLOAT,   --% Compuesto Princ.--
	-- Material characteristics
	bet_m2_g FLOAT,   --BET (m2/g)--
	thickness_nm INT,   --Espesor--
	size_material_nm INT,   --Tamaño--
	ratio VARCHAR ( 50 )   --Proporción--
);


-- CREATE TABLE 'solutions'
CREATE TABLE solutions_current (
	-- Description product
	ID INT PRIMARY KEY,
	id_solution VARCHAR ( 50 ) NOT NULL,   --id--
	name_solution VARCHAR ( 50 ) NOT NULL,   --Título--
	label VARCHAR ( 50 ) NOT NULL,   --Etiquetas--
	parent VARCHAR ( 50 ) NOT NULL,   --parent--
	url VARCHAR ( 50 ) NOT NULL,   --url--
	-- Researcher and manufacturer
	realized_by VARCHAR ( 50 ) NOT NULL,   --Realizado--
	record_created_by VARCHAR ( 50 ) NOT NULL,   --created_by--
	record_last_edited_by VARCHAR ( 50 ) NOT NULL,   --last_edited_by--
	-- Date
	record_created_time TIMESTAMP  NOT NULL,   --created_time--
	record_last_edited_time TIMESTAMP  NOT NULL,   --last_edited_time--
	preparation_date TIMESTAMP  NOT NULL,   --Preparación--
	load_ts TIMESTAMP  NOT NULL,
	-- Percentage and ratio
	ratio_materials VARCHAR ( 50 ) NOT NULL,   --Concentración--
	-- Relations
	id_solvent VARCHAR ( 50 ) NOT NULL,   --Disolvente--
	id_solute VARCHAR ( 50 ) NOT NULL,   --Soluto--
	id_dopant VARCHAR ( 50 ),   --Dopante--
	id_sensor VARCHAR ( 50 ) NOT NULL   --Sensor--
);


-- CREATE TABLE 'sensors'
CREATE TABLE sensors_current (
	-- Description product
	ID INT PRIMARY KEY,
	id_sensor VARCHAR ( 50 ),   --id-
	name_sensor VARCHAR ( 50 ) NOT NULL,   --Título-
	label VARCHAR ( 50 ) NOT NULL,   --Etiquetas-
	parent VARCHAR ( 50 ) NOT NULL,   --parent-
	url VARCHAR ( 50 ) NOT NULL,   --url-
	-- Researcher and manufacturer
	realized_by VARCHAR ( 50 ) NOT NULL,   --Realizado-
	sensor_type VARCHAR ( 50 ) NOT NULL,   --Tipo-
	record_created_by VARCHAR ( 50 ) NOT NULL,   --created_by-
	record_last_edited_by VARCHAR ( 50 ) NOT NULL,   --last_edited_by-
	-- Date
	record_created_time TIMESTAMP  NOT NULL,   --created_time-
	record_last_edited_time TIMESTAMP  NOT NULL,   --last_edited_time-
	load_ts TIMESTAMP  NOT NULL,
	-- Deposition parameters
	deposition_method VARCHAR ( 50 ),   --Método dep.-
	susbtrate_1 VARCHAR ( 50 ),   --Membrana 1-
	susbtrate_2 VARCHAR ( 50 ),   --Membrana 2-
	susbtrate_3 VARCHAR ( 50 ),   --Membrana 3-
	susbtrate_4 VARCHAR ( 50 ),   --Membrana 4-
	solutions_used VARCHAR ( 50 ),   --Disol. empleadas-
	deposition_parameters  VARCHAR ( 50 )   --Parámetros dep.-
);


-- CREATE TABLE 'leds'
CREATE TABLE leds_current (
	-- Description product
	ID INT PRIMARY KEY,
	id_led VARCHAR ( 50 ),   --id-
	name_led VARCHAR ( 50 ) NOT NULL,   --Led-
	parent VARCHAR ( 50 ) NOT NULL,   --parent-
	url VARCHAR ( 50 ) NOT NULL,   --url-
	-- Researcher and manufacturer
	record_created_by VARCHAR ( 50 ) NOT NULL,   --created_by-
	record_last_edited_by VARCHAR ( 50 ) NOT NULL,   --last_edited_by-
	-- Date
	record_created_time TIMESTAMP  NOT NULL,   --created_time-
	record_last_edited_time TIMESTAMP  NOT NULL,   --last_edited_time-
	load_ts TIMESTAMP  NOT NULL,
	-- Led characteristics
	voltage_V_used FLOAT NOT NULL,   --V/A utilizado-
	current_mA_used FLOAT NOT NULL,   --V/A utilizado-
	voltage_range  VARCHAR ( 50 ) NOT NULL,   --Voltaje-
	current_range  VARCHAR ( 50 ) NOT NULL,   --Corriente-
	wavelength_nm  FLOAT NOT NULL,   --Long. onda-
	optical_power_mW   FLOAT NOT NULL,   --Potencia Óptica-
	comments   VARCHAR ( 50 )   --Comentarios-
);


-- CREATE TABLE 'gases'
CREATE TABLE gases_current (
	-- Description product
	ID INT PRIMARY KEY,
	id_gas VARCHAR ( 50 ),   --id-
	name_gas VARCHAR ( 50 ) NOT NULL,   --Título-
	label VARCHAR ( 50 ) NOT NULL,   --Etiquetas-
	parent VARCHAR ( 50 ) NOT NULL,   --parent-
	url VARCHAR ( 50 ) NOT NULL,   --url-
	-- Researcher and manufacturer
	record_created_by VARCHAR ( 50 ) NOT NULL,   --created_by-
	record_last_edited_by VARCHAR ( 50 ) NOT NULL,   --last_edited_by-
	load_ts TIMESTAMP  NOT NULL,
	-- Date
	record_created_time TIMESTAMP  NOT NULL,   --created_time-
	record_last_edited_time TIMESTAMP  NOT NULL,   --last_edited_time-
	-- Characteristics
	max_concentration_ppb VARCHAR ( 50 ) NOT NULL   --Max. Concetración-
);


-- CREATE TABLE 'measurements'
CREATE TABLE measurements_hist (
	-- Description product
	ID INT PRIMARY KEY,
	conn_measurement VARCHAR ( 50 ) NOT NULL,
	id_measurement VARCHAR ( 50 ) NOT NULL,   --id-
	name_measurement VARCHAR ( 50 ) NOT NULL,   --Título-
	label VARCHAR ( 50 ),   --Gas-
	parent VARCHAR ( 50 ) NOT NULL,   --parent-
	url VARCHAR ( 50 ) NOT NULL,   --url-
	-- Researcher and manufacturer
	realized_by VARCHAR ( 50 ) NOT NULL,   --Realizado-
	record_created_by VARCHAR ( 50 ) NOT NULL,   --created_by-
	record_last_edited_by VARCHAR ( 50 ) NOT NULL,   --last_edited_by-
	-- Date
	record_created_time TIMESTAMP  NOT NULL,   --created_time-
	record_last_edited_time TIMESTAMP  NOT NULL,   --last_edited_time-
	load_ts TIMESTAMP  NOT NULL,
	-- Measurement characteristics
	project VARCHAR NOT NULL,   --Proyecto-
	concetrations_ppb VARCHAR ( 50 ) NOT NULL,   --Concentraciones-
	humidity_percentage FLOAT NOT NULL,   --Humedad-
	measurement_equipment VARCHAR ( 50 ) NOT NULL,   --Equipo medida-
	result_measurement VARCHAR ( 50 ),   --Resultado-
	gases_line_used VARCHAR ( 50 ) NOT NULL,   --Línea-
	-- Relations
	id_sensor VARCHAR ( 50 ) NOT NULL,   --Sensor-
	id_led VARCHAR ( 50 ),   --Led-
	id_gases VARCHAR ( 50 )   --Gases-
);



-- CREATE TABLE 'electrical_measurements'
CREATE TABLE data_line (
	ID INT PRIMARY KEY,
	file_title VARCHAR ( 50 ) NOT NULL,
	load_ts	TIMESTAMP NOT NULL,
	time_s FLOAT NOT NULL,   --Time [s]
	sensor1_ohm FLOAT NOT NULL,   --R1 [ohm]
	sensor2_ohm FLOAT NOT NULL,  --R2 [ohm]
	sensor3_ohm FLOAT NOT NULL,   --R3 [ohm]
	sensor4_ohm FLOAT NOT NULL,   --R4 [ohm]
	bottle1_ppb FLOAT NOT NULL,   --[Botella 1-Nada] [ppbv]
	bottle2_ppb FLOAT NOT NULL,   --[Botella 2-CO2] [ppbv]
	bottle3_ppb FLOAT NOT NULL,   --[Botella 3-Nada] [ppbv]
	date_timestamp TIMESTAMP,   --Time Stamp
	temperature_C FLOAT NOT NULL,   --Temperature [ºC]
	sensor1_heat_mV FLOAT NOT NULL,   --V Heating R1 [mV]
	sensor2_heat_mV FLOAT NOT NULL,   --V Heating R2 [mV]
	sensor3_heat_mV FLOAT NOT NULL,   --V Heating R3 [mV]	
	sensor4_heat_mV FLOAT NOT NULL,   --V Heating R4 [mV]	
	sensor1_heat_mA FLOAT NOT NULL,   --I Heating R1 [mA]	
	sensor2_heat_mA FLOAT NOT NULL,   --I Heating R2 [mA]	
	sensor3_heat_mA FLOAT NOT NULL,   --I Heating R3 [mA]	
	sensor4_heat_mA FLOAT NOT NULL,   --I Heating R4 [mA]	
	sensor1_heat_C FLOAT NOT NULL,   --T Heating R1 [ºC]		
	sensor2_heat_C FLOAT NOT NULL,   --T Heating R2 [ºC]	
	sensor3_heat_C FLOAT NOT NULL,   --T Heating R3 [ºC]	
	sensor4_heat_C FLOAT NOT NULL,   --T Heating R4 [ºC]
	c1_flow_ml_min FLOAT NOT NULL,   --C1 Flow [ml/min]
	c2_flow_ml_min FLOAT NOT NULL,   --C2 Flow [ml/min]
	c3_flow_ml_min FLOAT NOT NULL,   --C3 Flow [ml/min]
	c4_flow_ml_min FLOAT NOT NULL,   --C4 Flow [ml/min]
	c5_flow_ml_min FLOAT NOT NULL,   --C5 Flow [ml/min]
	c6_flow_ml_min FLOAT NOT NULL,   --Nada							
	polarization_voltage_V FLOAT NOT NULL,   --Voltaje Polarización [V]														
	humidity_percentage FLOAT NOT NULL,   --HR
	comments VARCHAR   --Untitled
);
	
	
-- CREATE TABLE 'optical_parameters'
CREATE TABLE optical_parameters (
	experiment_name VARCHAR ( 50 ) PRIMARY KEY,
	start_timestamp VARCHAR ( 50 ) NOT NULL,
	load_ts VARCHAR ( 50 ) NOT NULL,
	spectrometer VARCHAR ( 50 ) NOT NULL,
	trigger_mode FLOAT NOT NULL,
	integration_time_s FLOAT NOT NULL,
	scan_to_avg FLOAT NOT NULL,
	nonlinearity_corr INT NOT NULL,
	boxcar_width FLOAT NOT NULL,
	x_axis_node VARCHAR ( 50 ) NOT NULL,
	pixels_number INT NOT NULL
);


-- CREATE TABLE 'optical_parameters'
CREATE TABLE optical_spectra (
	ID  INT PRIMARY KEY,
	experiment_name VARCHAR ( 50 ) NOT NULL,
	current_timestamp  VARCHAR ( 50 ) NOT NULL,
	axis  VARCHAR ( 50 ) NOT NULL,
	spectra  TEXT ( 50 ) NOT NULL
);