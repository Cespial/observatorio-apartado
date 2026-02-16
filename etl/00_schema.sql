-- ============================================================
-- OBSERVATORIO DE CIUDADES — APARTADÓ
-- Schema de Base de Datos PostGIS
-- ============================================================

-- Esquemas temáticos
CREATE SCHEMA IF NOT EXISTS cartografia;
CREATE SCHEMA IF NOT EXISTS socioeconomico;
CREATE SCHEMA IF NOT EXISTS seguridad;
CREATE SCHEMA IF NOT EXISTS servicios;
CREATE SCHEMA IF NOT EXISTS catastro;
CREATE SCHEMA IF NOT EXISTS ambiental;

-- ============================================================
-- CARTOGRAFÍA BASE
-- ============================================================

CREATE TABLE IF NOT EXISTS cartografia.limite_municipal (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    divipola VARCHAR(10),
    departamento VARCHAR(100),
    area_km2 NUMERIC,
    geom GEOMETRY(Polygon, 4326)
);

CREATE TABLE IF NOT EXISTS cartografia.osm_edificaciones (
    id BIGINT PRIMARY KEY,
    osm_type VARCHAR(20),
    building VARCHAR(100),
    name VARCHAR(255),
    amenity VARCHAR(100),
    addr_street VARCHAR(255),
    geom GEOMETRY(Polygon, 4326)
);

CREATE TABLE IF NOT EXISTS cartografia.osm_vias (
    id BIGINT PRIMARY KEY,
    osm_type VARCHAR(20),
    highway VARCHAR(100),
    name VARCHAR(255),
    surface VARCHAR(100),
    lanes INTEGER,
    geom GEOMETRY(LineString, 4326)
);

CREATE TABLE IF NOT EXISTS cartografia.osm_uso_suelo (
    id BIGINT PRIMARY KEY,
    landuse VARCHAR(100),
    name VARCHAR(255),
    geom GEOMETRY(Polygon, 4326)
);

CREATE TABLE IF NOT EXISTS cartografia.osm_amenidades (
    id BIGINT PRIMARY KEY,
    amenity VARCHAR(100),
    name VARCHAR(255),
    phone VARCHAR(100),
    website VARCHAR(500),
    opening_hours VARCHAR(255),
    lat NUMERIC,
    lon NUMERIC,
    geom GEOMETRY(Point, 4326)
);

-- ============================================================
-- MGN — MANZANAS CENSALES
-- ============================================================

CREATE TABLE IF NOT EXISTS cartografia.manzanas_censales (
    id SERIAL PRIMARY KEY,
    cod_dane_manzana VARCHAR(30),
    cod_dane_seccion VARCHAR(20),
    cod_dane_sector VARCHAR(20),
    cod_dane_municipio VARCHAR(10),
    tipo VARCHAR(50),
    total_personas INTEGER,
    total_hogares INTEGER,
    total_viviendas INTEGER,
    viviendas_ocupadas INTEGER,
    personas_hombres INTEGER,
    personas_mujeres INTEGER,
    geom GEOMETRY(MultiPolygon, 4326)
);
CREATE INDEX IF NOT EXISTS idx_manzanas_municipio ON cartografia.manzanas_censales(cod_dane_municipio);
CREATE INDEX IF NOT EXISTS idx_manzanas_geom ON cartografia.manzanas_censales USING GIST(geom);

-- ============================================================
-- CATASTRO
-- ============================================================

CREATE TABLE IF NOT EXISTS catastro.terrenos (
    id SERIAL PRIMARY KEY,
    codigo_predial VARCHAR(50),
    municipio VARCHAR(100),
    cod_municipio VARCHAR(10),
    area_terreno NUMERIC,
    avaluo_catastral NUMERIC,
    destino_economico VARCHAR(100),
    geom GEOMETRY(MultiPolygon, 4326)
);
CREATE INDEX IF NOT EXISTS idx_terrenos_municipio ON catastro.terrenos(cod_municipio);
CREATE INDEX IF NOT EXISTS idx_terrenos_geom ON catastro.terrenos USING GIST(geom);

CREATE TABLE IF NOT EXISTS catastro.construcciones (
    id SERIAL PRIMARY KEY,
    codigo_predial VARCHAR(50),
    municipio VARCHAR(100),
    cod_municipio VARCHAR(10),
    area_construida NUMERIC,
    tipo_construccion VARCHAR(100),
    pisos INTEGER,
    geom GEOMETRY(MultiPolygon, 4326)
);

CREATE TABLE IF NOT EXISTS catastro.sectores (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50),
    nombre VARCHAR(255),
    municipio VARCHAR(100),
    geom GEOMETRY(MultiPolygon, 4326)
);

CREATE TABLE IF NOT EXISTS catastro.veredas (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50),
    nombre VARCHAR(255),
    municipio VARCHAR(100),
    area_ha NUMERIC,
    geom GEOMETRY(MultiPolygon, 4326)
);

-- ============================================================
-- SOCIOECONÓMICO
-- ============================================================

CREATE TABLE IF NOT EXISTS socioeconomico.ipm (
    id SERIAL PRIMARY KEY,
    cod_municipio VARCHAR(10),
    municipio VARCHAR(100),
    departamento VARCHAR(100),
    ipm_total NUMERIC,
    bajo_logro_educativo NUMERIC,
    analfabetismo NUMERIC,
    inasistencia_escolar NUMERIC,
    rezago_escolar NUMERIC,
    barreras_salud NUMERIC,
    sin_aseguramiento NUMERIC,
    sin_agua NUMERIC,
    sin_alcantarillado NUMERIC,
    pisos_inadecuados NUMERIC,
    paredes_inadecuadas NUMERIC,
    hacinamiento NUMERIC,
    trabajo_infantil NUMERIC,
    alta_dependencia NUMERIC,
    empleo_informal NUMERIC,
    sin_internet NUMERIC
);

CREATE TABLE IF NOT EXISTS socioeconomico.nbi (
    id SERIAL PRIMARY KEY,
    cod_municipio VARCHAR(10),
    municipio VARCHAR(100),
    departamento VARCHAR(100),
    nbi_total NUMERIC,
    nbi_urbano NUMERIC,
    nbi_rural NUMERIC,
    prop_miseria NUMERIC,
    comp_vivienda NUMERIC,
    comp_servicios NUMERIC,
    comp_hacinamiento NUMERIC,
    comp_inasistencia NUMERIC,
    comp_dependencia NUMERIC
);

CREATE TABLE IF NOT EXISTS socioeconomico.establecimientos_educativos (
    id SERIAL PRIMARY KEY,
    codigo_dane VARCHAR(20),
    nombre VARCHAR(255),
    municipio VARCHAR(100),
    cod_municipio VARCHAR(10),
    sector VARCHAR(50),
    calendario VARCHAR(20),
    direccion VARCHAR(255),
    telefono VARCHAR(50),
    total_matricula INTEGER,
    cantidad_sedes INTEGER
);

CREATE TABLE IF NOT EXISTS socioeconomico.icfes (
    id SERIAL PRIMARY KEY,
    periodo VARCHAR(20),
    cole_nombre VARCHAR(255),
    cole_cod_dane VARCHAR(20),
    cole_mcpio VARCHAR(100),
    punt_lectura_critica NUMERIC,
    punt_matematicas NUMERIC,
    punt_c_naturales NUMERIC,
    punt_sociales NUMERIC,
    punt_ingles NUMERIC,
    punt_global NUMERIC,
    estu_genero VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS socioeconomico.ips_salud (
    id SERIAL PRIMARY KEY,
    codigo_habilitacion VARCHAR(30),
    nombre VARCHAR(255),
    municipio VARCHAR(100),
    cod_municipio VARCHAR(10),
    departamento VARCHAR(100),
    clase_persona VARCHAR(50),
    nivel_atencion VARCHAR(20),
    caracter VARCHAR(50),
    direccion VARCHAR(255),
    telefono VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS socioeconomico.prestadores_servicios (
    id SERIAL PRIMARY KEY,
    nit VARCHAR(20),
    razon_social VARCHAR(255),
    municipio VARCHAR(100),
    cod_municipio VARCHAR(10),
    servicio VARCHAR(255),
    cobertura NUMERIC,
    suscriptores INTEGER
);

-- ============================================================
-- SEGURIDAD Y CONFLICTO
-- ============================================================

CREATE TABLE IF NOT EXISTS seguridad.homicidios (
    id SERIAL PRIMARY KEY,
    fecha DATE,
    municipio VARCHAR(100),
    cod_municipio VARCHAR(20),
    departamento VARCHAR(100),
    genero VARCHAR(20),
    grupo_etario VARCHAR(50),
    arma_medio VARCHAR(100),
    cantidad INTEGER
);

CREATE TABLE IF NOT EXISTS seguridad.hurtos (
    id SERIAL PRIMARY KEY,
    fecha DATE,
    municipio VARCHAR(100),
    cod_municipio VARCHAR(20),
    departamento VARCHAR(100),
    tipo_hurto VARCHAR(100),
    genero VARCHAR(20),
    grupo_etario VARCHAR(50),
    arma_medio VARCHAR(100),
    cantidad INTEGER
);

CREATE TABLE IF NOT EXISTS seguridad.delitos_sexuales (
    id SERIAL PRIMARY KEY,
    fecha DATE,
    municipio VARCHAR(100),
    cod_municipio VARCHAR(20),
    departamento VARCHAR(100),
    genero VARCHAR(20),
    grupo_etario VARCHAR(50),
    cantidad INTEGER
);

CREATE TABLE IF NOT EXISTS seguridad.violencia_intrafamiliar (
    id SERIAL PRIMARY KEY,
    fecha DATE,
    municipio VARCHAR(100),
    cod_municipio VARCHAR(20),
    departamento VARCHAR(100),
    genero VARCHAR(20),
    grupo_etario VARCHAR(50),
    arma_medio VARCHAR(100),
    cantidad INTEGER
);

CREATE TABLE IF NOT EXISTS seguridad.victimas_conflicto (
    id SERIAL PRIMARY KEY,
    cod_municipio VARCHAR(10),
    municipio VARCHAR(100),
    departamento VARCHAR(100),
    hecho VARCHAR(100),
    sexo VARCHAR(20),
    etnia VARCHAR(100),
    ciclo_vital VARCHAR(50),
    discapacidad VARCHAR(10),
    personas INTEGER,
    eventos INTEGER,
    fecha_corte DATE
);

-- ============================================================
-- GOOGLE PLACES
-- ============================================================

CREATE TABLE IF NOT EXISTS servicios.google_places (
    id SERIAL PRIMARY KEY,
    place_id VARCHAR(255) UNIQUE,
    name VARCHAR(500),
    category VARCHAR(100),
    types TEXT[],
    address VARCHAR(500),
    rating NUMERIC,
    user_ratings_total INTEGER,
    price_level INTEGER,
    phone VARCHAR(50),
    website VARCHAR(500),
    lat NUMERIC,
    lon NUMERIC,
    geom GEOMETRY(Point, 4326)
);
CREATE INDEX IF NOT EXISTS idx_places_geom ON servicios.google_places USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_places_category ON servicios.google_places(category);

-- ============================================================
-- VISTAS MATERIALIZADAS para cruces rápidos
-- ============================================================

-- Se crearán después de cargar datos
