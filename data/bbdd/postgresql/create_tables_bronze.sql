-- CREATE SCHEMA IF NOT EXISTS
CREATE SCHEMA IF NOT EXISTS bronze;

-- CREATE TABLE 'ingestion_log' -- Tabla para registrar las ingestas de archivos con metadatos
CREATE TABLE bronze.ingestion_log (
    -- Usamos SERIAL para que el ID se autoincremente solo
    ID SERIAL PRIMARY KEY,
    
    -- Identificadores únicos
    experiment_id VARCHAR(50) UNIQUE NOT NULL, -- El MED-XXX
    notion_page_id UUID,                       -- Las IDs de Notion suelen ser formato UUID
    
    -- Referencias a Google Drive
    drive_file_id_tdms VARCHAR(255),    -- ID del archivo TDMS original en Drive
    drive_file_id_parquet VARCHAR(255), -- ID del archivo Parquet generado en Drive
    
    -- Timestamps (con zona horaria)
    ingestion_timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    tdms_last_modified TIMESTAMPTZ,
    
    -- Metadatos técnicos
    script_version VARCHAR(20),
    file_size_bytes BIGINT,        -- BIGINT por si el archivo es muy pesado
    file_hash VARCHAR(64),         -- Para hashes SHA-256
    
    -- Estado del proceso
    status VARCHAR(20) CHECK (status IN ('SUCCESS', 'FAILED', 'PENDING'))
);