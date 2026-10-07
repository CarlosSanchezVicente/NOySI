-- CREATE TABLE 'data_processed' -- hist
CREATE TABLE data_processed (
    ID INT PRIMARY KEY,
    file_title VARCHAR ( 50 ) NOT NULL,
    load_ts TIMESTAMP  NOT NULL,   --Time [s]
    time_s TIMESTAMP  NOT NULL,   --Time [s]
    date_timestamp TIMESTAMP  NOT NULL,   --Time [s]
    sensor1_ohm FLOAT NOT NULL,   --R1 [ohm]
    sensor2_ohm FLOAT NOT NULL,   --R2 [ohm]
    sensor3_ohm FLOAT NOT NULL,   --R3 [ohm]
    sensor4_ohm FLOAT NOT NULL,   --R4 [ohm]
    bottle1_ppb FLOAT NOT NULL,   --[Botella 1-Nada] [ppbv]
    bottle2_ppb FLOAT NOT NULL,   --[Botella 2-Nada] [ppbv]
    bottle3_ppb FLOAT NOT NULL,   --[Botella 3-Nada] [ppbv]
    bottle_ppb_desplaced FLOAT NOT NULL,   --[Botella-desplaced] [ppbv]
    s1_drift_curve FLOAT NOT NULL,   --R1 [ohm]
    s1_drift_curve_corr FLOAT NOT NULL,   --R1 [ohm]
    s1_without_drift FLOAT NOT NULL,   --R1 [ohm]
    s2_drift_curve FLOAT NOT NULL,   --R2 [ohm]
    s2_drift_curve_corr FLOAT NOT NULL,   --R2 [ohm]
    s2_without_drift FLOAT NOT NULL,   --R2 [ohm]
    s3_drift_curve FLOAT NOT NULL,   --R3 [ohm]
    s3_drift_curve_corr FLOAT NOT NULL,   --R3 [ohm]
    s3_without_drift FLOAT NOT NULL,   --R3 [ohm]
    s4_drift_curve FLOAT NOT NULL,   --R4 [ohm]
    s4_drift_curve_corr FLOAT NOT NULL,   --R4 [ohm]
    s4_without_drift FLOAT NOT NULL,   --R4 [ohm]
);


-- CREATE TABLE 'data_pos' -- hist
CREATE TABLE data_pos (
    ID INT PRIMARY KEY,
    file_title VARCHAR ( 50 ) NOT NULL,
    init_pos INT NOT NULL,   --Position in matrix      
    final_pos INT NOT NULL,   --Position in matrix
    bottle_cycle_ppb INT NOT NULL,   --[ppbv]
    final_date_timestamp TIMESTAMP  NOT NULL   --Time [s]
);


-- CREATE TABLE 'data_response' -- hist
CREATE TABLE data_response (
    ID INT PRIMARY KEY,
    file_title VARCHAR ( 50 ) NOT NULL,
    concentration_ppb FLOAT NOT NULL,   --[ppbv]
    s1_without_drift FLOAT NOT NULL,   --[ohm]
    s1_measurable_range FLOAT NOT NULL,   --[ppm]
    s1_linear_range FLOAT NOT NULL,   --[ppm]
    s1_sensibility FLOAT NOT NULL,   --[%/ppm]
    s1_r_squared  FLOAT NOT NULL,
    s1_rms FLOAT NOT NULL,   --[ppm-1]
    s1_lod FLOAT NOT NULL,   --[ppm]
    s1_response_time  FLOAT NOT NULL,   --[s]
    s1_recovery_time  FLOAT NOT NULL,   --[s]
    s2_without_drift FLOAT NOT NULL,
    s2_measurable_range FLOAT NOT NULL,   --[ppm]
    s2_linear_range FLOAT NOT NULL,   --[ppm]
    s2_sensibility FLOAT NOT NULL,   --[%/ppm]
    s2_r_squared  FLOAT NOT NULL,
    s2_rms FLOAT NOT NULL,   --[ppm-1]
    s2_lod FLOAT NOT NULL,   --[ppm]
    s2_response_time  FLOAT NOT NULL,   --[s]
    s2_recovery_time  FLOAT NOT NULL,   --[s]
    s3_without_drift FLOAT NOT NULL,
    s3_measurable_range FLOAT NOT NULL,   --[ppm]
    s3_linear_range FLOAT NOT NULL,   --[ppm]
    s3_sensibility FLOAT NOT NULL,   --[%/ppm]
    s3_r_squared  FLOAT NOT NULL,
    s3_rms FLOAT NOT NULL,   --[ppm-1]
    s3_lod FLOAT NOT NULL,   --[ppm]
    s3_response_time  FLOAT NOT NULL,   --[s]
    s3_recovery_time  FLOAT NOT NULL,   --[s]
    s4_without_drift FLOAT NOT NULL,
    s4_measurable_range FLOAT NOT NULL,   --[ppm]
    s4_linear_range FLOAT NOT NULL,   --[ppm]
    s4_sensibility FLOAT NOT NULL,   --[%/ppm]
    s4_r_squared  FLOAT NOT NULL,
    s4_rms FLOAT NOT NULL,   --[ppm-1]
    s4_lod FLOAT NOT NULL,   --[ppm]
    s4_response_time  FLOAT NOT NULL,   --[s]
    s4_recovery_time  FLOAT NOT NULL,   --[s]
);