-- CREATE SCHEMA IF NOT EXISTS gold;

-- CREATE TABLE 'data_processed' -- hist
CREATE TABLE gold.data_processed (
    id SERIAL PRIMARY KEY,
    file_title VARCHAR ( 100 ) NOT NULL,
    load_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,   --Time [s]
    time_s TIMESTAMP NOT NULL,              --Time [s]
    date_timestamp TIMESTAMP NOT NULL,      --Time [s]
    sensor1_ohm FLOAT NOT NULL,             --R1 [ohm]
    sensor2_ohm FLOAT NOT NULL,             --R2 [ohm]
    sensor3_ohm FLOAT NOT NULL,             --R3 [ohm]
    sensor4_ohm FLOAT NOT NULL,             --R4 [ohm]
    bottle1_ppb FLOAT NOT NULL,             --[Botella 1-Nada] [ppbv]
    bottle2_ppb FLOAT NOT NULL,             --[Botella 2-Nada] [ppbv]
    bottle3_ppb FLOAT NOT NULL,             --[Botella 3-Nada] [ppbv]
    bottle_ppb_desplaced FLOAT NOT NULL,    --[Botella-desplaced] [ppbv]
    s1_drift_curve FLOAT NOT NULL,          --R1 [ohm]
    s1_drift_curve_corr FLOAT NOT NULL,     --R1 [ohm]
    s1_without_drift FLOAT NOT NULL,        --R1 [ohm]
    s2_drift_curve FLOAT NOT NULL,          --R2 [ohm]
    s2_drift_curve_corr FLOAT NOT NULL,     --R2 [ohm]
    s2_without_drift FLOAT NOT NULL,        --R2 [ohm]
    s3_drift_curve FLOAT NOT NULL,          --R3 [ohm]
    s3_drift_curve_corr FLOAT NOT NULL,     --R3 [ohm]
    s3_without_drift FLOAT NOT NULL,        --R3 [ohm]
    s4_drift_curve FLOAT NOT NULL,          --R4 [ohm]
    s4_drift_curve_corr FLOAT NOT NULL,     --R4 [ohm]
    s4_without_drift FLOAT NOT NULL         --R4 [ohm]
);


-- CREATE TABLE 'data_pos' -- hist
CREATE TABLE gold.data_pos (
    id SERIAL PRIMARY KEY,
    file_title VARCHAR ( 100 ) NOT NULL,
    init_pos INT NOT NULL,                    --Position in matrix      
    final_pos INT NOT NULL,                   --Position in matrix
    bottle_cycle_ppb INT NOT NULL,            --[ppbv]
    final_date_timestamp TIMESTAMP NOT NULL   --Time [s]
);


CREATE TABLE gold.data_response (
    id SERIAL PRIMARY KEY,
    file_title VARCHAR ( 100 ) NOT NULL,   -- MED-XXX
    gas VARCHAR ( 50 ) NOT NULL,           -- Gas medido
    sensor VARCHAR ( 20 ) NOT NULL,        -- 'sensor1', 'sensor2', etc. (Categoría)
    
    -- Métricas de Calidad
    concentration_ppb FLOAT NOT NULL,      -- [ppbv]
    mean_resistance_ohm FLOAT,             -- Resistencia promedio en el paso
    rms_noise FLOAT,                       -- Ruido [ppm-1]
    n_points INT,                          -- Puntos usados para el cálculo
    removed_outliers INT,              -- Outliers eliminados
    
    -- Resultados de la Regresión
    slope FLOAT,                           -- Pendiente de la curva
    r2_linear FLOAT,                       -- Coeficiente R2
    lod_ppb FLOAT,                         -- Límite de detección
    loq_ppb FLOAT,                         -- Límite de cuantificación
    
    -- Rangos y Sensibilidad
    linear_range_min_ppm FLOAT,                -- Rango lineal
    linear_range_max_ppm FLOAT,                -- Rango lineal
    measurable_range_min_ppm FLOAT,            -- Rango medible
    measurable_range_max_ppm FLOAT,            -- Rango medible
    sensitivity_percent_ppm FLOAT,         -- [%/ppm]
    
    -- Tiempos de Respuesta
    response_time_min FLOAT,               -- [min]
    recovery_time_min FLOAT,               -- [min]
    
    load_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);