-- Paso 1: Agregar una nueva columna con el tipo VARCHAR
ALTER TABLE materials
ADD COLUMN preparation_date_new VARCHAR(50);

-- Paso 2: Copiar datos de la columna original a la nueva columna
--UPDATE materials
--SET preparation_date_new = CAST(preparation_date AS VARCHAR(50));

ALTER TABLE materials
DROP COLUMN ID;

-- Paso 4: Cambiar el nombre de la nueva columna al nombre original
ALTER TABLE materials
RENAME COLUMN preparation_date_new TO preparation_date;