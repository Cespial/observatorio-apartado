-- ============================================================
-- DB OPTIMIZATION — INFRASTRUCTURE & SCALABILITY
-- Mission: Support 10x data expansion and traffic
-- ============================================================

-- 1. PostGIS Optimization for Regional Aggregations
-- Increase memory for complex spatial joins
ALTER SYSTEM SET work_mem = '64MB';
ALTER SYSTEM SET maintenance_work_mem = '256MB';
ALTER SYSTEM SET max_parallel_workers_per_gather = '4';

-- 2. Standardized Large Tables (SIVIGILA, SISBEN, RIPS)
-- These tables are designed for high-performance querying and regional expansion

-- SIVIGILA (Vigilancia Epidemiológica)
CREATE TABLE IF NOT EXISTS socioeconomico.sivigila_consolidado (
    id SERIAL PRIMARY KEY,
    dane_code VARCHAR(10),
    fecha DATE,
    evento_nombre VARCHAR(255),
    evento_codigo VARCHAR(20),
    conteo_casos INTEGER,
    geom GEOMETRY(Point, 4326)
);

-- Compound Index for fast filtering by municipality and time
CREATE INDEX IF NOT EXISTS idx_sivigila_dane_fecha 
ON socioeconomico.sivigila_consolidado (dane_code, fecha);

-- SISBEN (Sistema de Identificación de Potenciales Beneficiarios)
CREATE TABLE IF NOT EXISTS socioeconomico.sisben_consolidado (
    id SERIAL PRIMARY KEY,
    dane_code VARCHAR(10),
    fecha DATE,
    grupo_sisben VARCHAR(5), -- A, B, C, D
    puntaje NUMERIC,
    conteo_personas INTEGER,
    geom GEOMETRY(Point, 4326)
);

CREATE INDEX IF NOT EXISTS idx_sisben_dane_fecha 
ON socioeconomico.sisben_consolidado (dane_code, fecha);

-- RIPS (Registros Individuales de Prestación de Servicios de Salud)
CREATE TABLE IF NOT EXISTS socioeconomico.rips_consolidado (
    id SERIAL PRIMARY KEY,
    dane_code VARCHAR(10),
    fecha DATE,
    cie10_codigo VARCHAR(10),
    tipo_servicio VARCHAR(100),
    conteo_atenciones INTEGER,
    valor_total NUMERIC
);

CREATE INDEX IF NOT EXISTS idx_rips_dane_fecha 
ON socioeconomico.rips_consolidado (dane_code, fecha);

-- 3. Optimization for existing Raw Tables (Sprint 1)
-- SIVIGILA Raw
CREATE INDEX IF NOT EXISTS idx_sivigila_raw_mun_ano 
ON socioeconomico.sivigila_raw (cod_mun, ano);

-- SECOP (Contratación Pública) - Very Large
CREATE INDEX IF NOT EXISTS idx_secop_tipo_valor 
ON servicios.secop_raw (tipo_de_contrato, valor_contrato);

-- 4. Materialized Views for Heatmaps (Optimized Geometries)
-- Simplification of geometries on the fly for regional views
CREATE MATERIALIZED VIEW IF NOT EXISTS cartografia.limite_municipal_simple AS
SELECT id, nombre, divipola, ST_Simplify(geom, 0.001) as geom_simple
FROM cartografia.limite_municipal;

CREATE INDEX IF NOT EXISTS idx_limite_simple_geom ON cartografia.limite_municipal_simple USING GIST(geom_simple);

-- 5. Maintenance
VACUUM ANALYZE socioeconomico.sivigila_raw;
VACUUM ANALYZE servicios.secop_raw;
