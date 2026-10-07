-- CREATE SCHEMA IF NOT EXISTS
CREATE SCHEMA IF NOT EXISTS silver;

-- CREATE TABLE 'materials'
CREATE TABLE silver.materials_current (
    id SERIAL PRIMARY KEY,
    id_material VARCHAR ( 100 ) NOT NULL,   --id
    name_material VARCHAR ( 255 ) NOT NULL,   --Título
    label VARCHAR ( 255 ) NOT NULL,   --Etiquetas
    parent VARCHAR ( 100 ) NOT NULL,   --parent
    url TEXT NOT NULL,   --url
    -- Researcher and manufacturer
    realized_by VARCHAR ( 100 ),   --Realizado
    manufacturer VARCHAR ( 100 ) NOT NULL,   --Fabricante
    material_type VARCHAR ( 100 ) NOT NULL,   --Tipo
    record_created_by VARCHAR ( 100 ) NOT NULL,   --created_by
    record_last_edited_by VARCHAR ( 100 ) NOT NULL,   --last_edited_by
    -- Date
    record_created_time TIMESTAMP NOT NULL,   --created_time
    record_last_edited_time TIMESTAMP NOT NULL,   --last_edited_time
    preparation_date VARCHAR ( 100 ) NOT NULL,   --Preparación
    load_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    -- Percentage and ratio
    others_compounds TEXT,   --Otros compuestos
    n_percentage FLOAT,   --%N
    h_percentage FLOAT,   --%H
    o_percentage FLOAT,   --%O
    main_comp_percentage FLOAT,   --% Compuesto Princ.
    -- Material characteristics
    bet_m2_g FLOAT,   --BET (m2/g)
    thickness_nm INT,   --Espesor
    size_material_nm INT,   --Tamaño
    ratio VARCHAR ( 100 )   --Proporción
);

-- CREATE TABLE 'solutions'
CREATE TABLE silver.solutions_current (
    id SERIAL PRIMARY KEY,
    id_solution VARCHAR ( 100 ) NOT NULL,   --id
    name_solution VARCHAR ( 255 ) NOT NULL,   --Título
    label VARCHAR ( 255 ) NOT NULL,   --Etiquetas
    parent VARCHAR ( 100 ) NOT NULL,   --parent
    url TEXT NOT NULL,   --url
    -- Researcher and manufacturer
    realized_by VARCHAR ( 100 ) NOT NULL,   --Realizado
    record_created_by VARCHAR ( 100 ) NOT NULL,   --created_by
    record_last_edited_by VARCHAR ( 100 ) NOT NULL,   --last_edited_by
    -- Date
    record_created_time TIMESTAMP NOT NULL,   --created_time
    record_last_edited_time TIMESTAMP NOT NULL,   --last_edited_time
    preparation_date TIMESTAMP NOT NULL,   --Preparación
    load_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    -- Percentage and ratio
    ratio_materials VARCHAR ( 100 ) NOT NULL,   --Concentración
    -- Relations
    id_solvent VARCHAR ( 100 ) NOT NULL,   --Disolvente
    id_solute VARCHAR ( 100 ) NOT NULL,   --Soluto
    id_dopant VARCHAR ( 100 ),   --Dopante
    id_sensor VARCHAR ( 100 ) NOT NULL   --Sensor
);

-- CREATE TABLE 'sensors'
CREATE TABLE silver.sensors_current (
    id SERIAL PRIMARY KEY,
    id_sensor VARCHAR ( 100 ),   --id
    name_sensor VARCHAR ( 255 ) NOT NULL,   --Título
    label VARCHAR ( 255 ) NOT NULL,   --Etiquetas
    parent VARCHAR ( 100 ) NOT NULL,   --parent
    url TEXT NOT NULL,   --url
    -- Researcher and manufacturer
    realized_by VARCHAR ( 100 ) NOT NULL,   --Realizado
    sensor_type VARCHAR ( 100 ) NOT NULL,   --Tipo
    record_created_by VARCHAR ( 100 ) NOT NULL,   --created_by
    record_last_edited_by VARCHAR ( 100 ) NOT NULL,   --last_edited_by
    -- Date
    record_created_time TIMESTAMP NOT NULL,   --created_time
    record_last_edited_time TIMESTAMP NOT NULL,   --last_edited_time
    load_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    -- Deposition parameters
    deposition_method VARCHAR ( 100 ),   --Método dep.
    substrate_1 VARCHAR ( 100 ),   --Membrana 1
    substrate_2 VARCHAR ( 100 ),   --Membrana 2
    substrate_3 VARCHAR ( 100 ),   --Membrana 3
    substrate_4 VARCHAR ( 100 ),   --Membrana 4
    solutions_used TEXT,   --Disol. empleadas
    deposition_parameters TEXT    --Parámetros dep.
);

-- CREATE TABLE 'leds'
CREATE TABLE silver.leds_current (
    id SERIAL PRIMARY KEY,
    id_led VARCHAR ( 100 ),   --id
    name_led VARCHAR ( 255 ) NOT NULL,   --Led
    parent VARCHAR ( 100 ) NOT NULL,   --parent
    url TEXT NOT NULL,   --url
    -- Researcher and manufacturer
    record_created_by VARCHAR ( 100 ) NOT NULL,   --created_by
    record_last_edited_by VARCHAR ( 100 ) NOT NULL,   --last_edited_by
    -- Date
    record_created_time TIMESTAMP NOT NULL,   --created_time
    record_last_edited_time TIMESTAMP NOT NULL,   --last_edited_time
    load_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    -- Led characteristics
    voltage_v_used FLOAT NOT NULL,   --V/A utilizado
    current_ma_used FLOAT NOT NULL,   --V/A utilizado
    voltage_range VARCHAR ( 100 ) NOT NULL,   --Voltaje
    current_range VARCHAR ( 100 ) NOT NULL,   --Corriente
    wavelength_nm FLOAT NOT NULL,   --Long. onda
    optical_power_mw FLOAT NOT NULL,   --Potencia Óptica
    comments TEXT   --Comentarios
);

-- CREATE TABLE 'gases'
CREATE TABLE silver.gases_current (
    id SERIAL PRIMARY KEY,
    id_gas VARCHAR ( 100 ),   --id
    name_gas VARCHAR ( 255 ) NOT NULL,   --Título
    label VARCHAR ( 255 ) NOT NULL,   --Etiquetas
    parent VARCHAR ( 100 ) NOT NULL,   --parent
    url TEXT NOT NULL,   --url
    -- Researcher and manufacturer
    record_created_by VARCHAR ( 100 ) NOT NULL,   --created_by
    record_last_edited_by VARCHAR ( 100 ) NOT NULL,   --last_edited_by
    load_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    -- Date
    record_created_time TIMESTAMP NOT NULL,   --created_time
    record_last_edited_time TIMESTAMP NOT NULL,   --last_edited_time
    -- Characteristics
    max_concentration_ppb VARCHAR ( 100 ) NOT NULL   --Max. Concetración
);

-- CREATE TABLE 'measurements'
CREATE TABLE silver.measurements_current (
    id SERIAL PRIMARY KEY,
    conn_measurement VARCHAR ( 100 ) NOT NULL,
    id_measurement VARCHAR ( 100 ) NOT NULL,   --id
    name_measurement VARCHAR ( 255 ) NOT NULL,   --Título
    label VARCHAR ( 255 ),   --Gas
    parent VARCHAR ( 100 ) NOT NULL,   --parent
    url TEXT NOT NULL,   --url
    -- Researcher and manufacturer
    realized_by VARCHAR ( 100 ) NOT NULL,   --Realizado
    record_created_by VARCHAR ( 100 ) NOT NULL,   --created_by
    record_last_edited_by VARCHAR ( 100 ) NOT NULL,   --last_edited_by
    -- Date
    record_created_time TIMESTAMP NOT NULL,   --created_time
    record_last_edited_time TIMESTAMP NOT NULL,   --last_edited_time
    load_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    -- Measurement characteristics
    project TEXT NOT NULL,   --Proyecto
    concentrations_ppb VARCHAR ( 100 ) NOT NULL,   --Concentraciones
    humidity_percentage FLOAT NOT NULL,   --Humedad
    measurement_equipment VARCHAR ( 100 ) NOT NULL,   --Equipo medida
    result_measurement TEXT,   --Resultado
    gases_line_used VARCHAR ( 100 ) NOT NULL,   --Línea
    -- Relations
    id_sensor VARCHAR ( 100 ) NOT NULL,   --Sensor
    id_led VARCHAR ( 100 ),   --Led
    id_gases VARCHAR ( 100 )    --Gases
);

-- CREATE TABLE 'electrical_measurements'
CREATE TABLE silver.data_line (
    id SERIAL PRIMARY KEY,
    file_title VARCHAR ( 100 ) NOT NULL,
    gas_step INT NOT NULL,  --Variable que marca el cambio de experimento para un mismo MED-XXX
    load_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    time_s FLOAT NOT NULL,   --Time [s]
    sensor1_ohm FLOAT NOT NULL,   --R1 [ohm]
    sensor2_ohm FLOAT NOT NULL,  --R2 [ohm]
    sensor3_ohm FLOAT NOT NULL,   --R3 [ohm]
    sensor4_ohm FLOAT NOT NULL,   --R4 [ohm]
    bottle1_ppb FLOAT NOT NULL,   --[Botella 1-Nada] [ppbv]
    bottle2_ppb FLOAT NOT NULL,   --[Botella 2-CO2] [ppbv]
    bottle3_ppb FLOAT NOT NULL,   --[Botella 3-Nada] [ppbv]
    date_timestamp TIMESTAMP,   --Time Stamp
    temperature_c FLOAT NOT NULL,   --Temperature [ºC]
    sensor1_heat_mv FLOAT NOT NULL,   --V Heating R1 [mV]
    sensor2_heat_mv FLOAT NOT NULL,   --V Heating R2 [mV]
    sensor3_heat_mv FLOAT NOT NULL,   --V Heating R3 [mV]   
    sensor4_heat_mv FLOAT NOT NULL,   --V Heating R4 [mV]   
    sensor1_heat_ma FLOAT NOT NULL,   --I Heating R1 [mA]   
    sensor2_heat_ma FLOAT NOT NULL,   --I Heating R2 [mA]   
    sensor3_heat_ma FLOAT NOT NULL,   --I Heating R3 [mA]   
    sensor4_heat_ma FLOAT NOT NULL,   --I Heating R4 [mA]   
    sensor1_heat_c FLOAT NOT NULL,   --T Heating R1 [ºC]        
    sensor2_heat_c FLOAT NOT NULL,   --T Heating R2 [ºC]    
    sensor3_heat_c FLOAT NOT NULL,   --T Heating R3 [ºC]    
    sensor4_heat_c FLOAT NOT NULL,   --T Heating R4 [ºC]
    c1_flow_ml_min FLOAT NOT NULL,   --C1 Flow [ml/min]
    c2_flow_ml_min FLOAT NOT NULL,   --C2 Flow [ml/min]
    c3_flow_ml_min FLOAT NOT NULL,   --C3 Flow [ml/min]
    c4_flow_ml_min FLOAT NOT NULL,   --C4 Flow [ml/min]
    c5_flow_ml_min FLOAT NOT NULL,   --C5 Flow [ml/min]
    c6_flow_ml_min FLOAT NOT NULL,   --C6 Flow [ml/min]
    polarization_voltage_v FLOAT NOT NULL,   --Voltaje Polarización [V]                                                                     
    hr_setpoint_percentage  FLOAT NOT NULL,   --HR Setpoint
	hr_read_percentage  FLOAT NOT NULL,   --HR Lectura
    comments TEXT   --Untitled
);


-- CREATE TABLE 'optical_parameters'
CREATE TABLE optical_parameters (
	experiment_name VARCHAR ( 50 ) PRIMARY KEY,	-- MED-XXX
	start_timestamp VARCHAR ( 50 ) NOT NULL,	--Time [s]
	load_ts VARCHAR ( 50 ) NOT NULL,			--Time [s]
	spectrometer VARCHAR ( 50 ) NOT NULL,	--Spectrometer
	trigger_mode FLOAT NOT NULL,		--Trigger mode
	integration_time_s FLOAT NOT NULL,	--Integration time [s]
	number_averages INT NOT NULL,		--Number averages	
	scan_to_avg FLOAT NOT NULL,	--Scan to avg
	nonlinearity_corr INT NOT NULL,	--Nonlinearity correction
	boxcar_width FLOAT NOT NULL,	--Boxcar width
	x_axis_node VARCHAR ( 50 ) NOT NULL,	--X axis node
	pixels_number INT NOT NULL	--Pixels number
);


-- CREATE TABLE 'optical_parameters'
CREATE TABLE optical_spectra (
	ID  INT PRIMARY KEY,
	experiment_name VARCHAR ( 50 ) NOT NULL,	-- MED-XXX
	current_timestamp  VARCHAR ( 50 ) NOT NULL,	--Time [s]
	axis  VARCHAR ( 50 ) NOT NULL,	--Axis
	spectra  TEXT ( 50 ) NOT NULL	--Spectra
);