"""
Endpoints de indicadores socioeconómicos, educativos, seguridad
"""
from fastapi import APIRouter, Query
from ..database import engine
from sqlalchemy import text
import json

router = APIRouter(prefix="/api/indicators", tags=["Indicadores"])


INDICATORS_CATALOG = [
    {
        "id": "icfes_global",
        "name": "Puntaje ICFES Global",
        "description": "Puntaje global promedio Saber 11 por colegio y periodo",
        "source": "ICFES via datos.gov.co",
        "unit": "puntos (0-500)",
        "category": "educacion",
    },
    {
        "id": "icfes_matematicas",
        "name": "Puntaje ICFES Matemáticas",
        "description": "Puntaje promedio de matemáticas Saber 11",
        "source": "ICFES via datos.gov.co",
        "unit": "puntos (0-100)",
        "category": "educacion",
    },
    {
        "id": "icfes_lectura",
        "name": "Puntaje ICFES Lectura Crítica",
        "description": "Puntaje promedio de lectura crítica Saber 11",
        "source": "ICFES via datos.gov.co",
        "unit": "puntos (0-100)",
        "category": "educacion",
    },
    {
        "id": "homicidios",
        "name": "Homicidios",
        "description": "Total de homicidios por año",
        "source": "Min. Defensa via datos.gov.co",
        "unit": "casos",
        "category": "seguridad",
    },
    {
        "id": "hurtos",
        "name": "Hurtos",
        "description": "Total de hurtos por año y tipo",
        "source": "DIJIN via datos.gov.co",
        "unit": "casos",
        "category": "seguridad",
    },
    {
        "id": "delitos_sexuales",
        "name": "Delitos Sexuales",
        "description": "Total de delitos sexuales por año",
        "source": "DIJIN via datos.gov.co",
        "unit": "casos",
        "category": "seguridad",
    },
    {
        "id": "violencia_intrafamiliar",
        "name": "Violencia Intrafamiliar",
        "description": "Total de casos de VIF por año",
        "source": "DIJIN via datos.gov.co",
        "unit": "casos",
        "category": "seguridad",
    },
    {
        "id": "victimas_conflicto",
        "name": "Víctimas del Conflicto",
        "description": "Personas afectadas por el conflicto armado por hecho victimizante",
        "source": "Unidad de Víctimas via datos.gov.co",
        "unit": "personas",
        "category": "conflicto",
    },
    {
        "id": "poblacion_manzana",
        "name": "Población por Manzana",
        "description": "Total de personas por manzana censal",
        "source": "DANE Censo 2018 / MGN",
        "unit": "personas",
        "category": "demografia",
    },
    {
        "id": "establecimientos_educativos",
        "name": "Establecimientos Educativos",
        "description": "Colegios y sedes educativas con matrícula",
        "source": "MEN via datos.gov.co",
        "unit": "establecimientos",
        "category": "educacion",
    },
    {
        "id": "ips_salud",
        "name": "IPS / Instituciones de Salud",
        "description": "Instituciones prestadoras de servicios de salud habilitadas",
        "source": "Min. Salud REPS via datos.gov.co",
        "unit": "sedes",
        "category": "salud",
    },
    {
        "id": "places_economia",
        "name": "Establecimientos Comerciales",
        "description": "Negocios por categoría (restaurantes, bancos, tiendas, etc)",
        "source": "Google Places API",
        "unit": "establecimientos",
        "category": "economia",
    },
]


@router.get("")
def list_indicators():
    """Listar todos los indicadores disponibles."""
    return INDICATORS_CATALOG


@router.get("/icfes")
def get_icfes(
    periodo: str = Query(None, description="Filtrar por periodo (ej: '20224')"),
    colegio: str = Query(None, description="Filtrar por nombre de colegio"),
    aggregate: str = Query("colegio", description="Nivel de agregación: 'colegio', 'periodo', 'genero'"),
):
    """Resultados ICFES Saber 11 con múltiples niveles de agregación."""
    if aggregate == "periodo":
        sql = """
            SELECT periodo,
                   COUNT(*) as estudiantes,
                   AVG(CAST(punt_global AS FLOAT)) as prom_global,
                   AVG(CAST(punt_matematicas AS FLOAT)) as prom_matematicas,
                   AVG(CAST(punt_lectura_critica AS FLOAT)) as prom_lectura,
                   AVG(CAST(punt_c_naturales AS FLOAT)) as prom_ciencias,
                   AVG(CAST(punt_sociales_ciudadanas AS FLOAT)) as prom_sociales,
                   AVG(CAST(punt_ingles AS FLOAT)) as prom_ingles
            FROM socioeconomico.icfes_raw
            GROUP BY periodo
            ORDER BY periodo
        """
        params = {}
    elif aggregate == "genero":
        sql = """
            SELECT estu_genero as genero, periodo,
                   COUNT(*) as estudiantes,
                   AVG(CAST(punt_global AS FLOAT)) as prom_global,
                   AVG(CAST(punt_matematicas AS FLOAT)) as prom_matematicas,
                   AVG(CAST(punt_lectura_critica AS FLOAT)) as prom_lectura
            FROM socioeconomico.icfes_raw
            WHERE estu_genero IS NOT NULL
            GROUP BY estu_genero, periodo
            ORDER BY periodo, genero
        """
        params = {}
    else:
        conditions = ["1=1"]
        params = {}
        if periodo:
            conditions.append("periodo = :p")
            params["p"] = periodo
        if colegio:
            conditions.append("cole_nombre_establecimiento ILIKE :c")
            params["c"] = f"%{colegio}%"
        where = " AND ".join(conditions)
        sql = f"""
            SELECT cole_nombre_establecimiento as colegio, periodo,
                   COUNT(*) as estudiantes,
                   AVG(CAST(punt_global AS FLOAT)) as prom_global,
                   AVG(CAST(punt_matematicas AS FLOAT)) as prom_matematicas,
                   AVG(CAST(punt_lectura_critica AS FLOAT)) as prom_lectura,
                   AVG(CAST(punt_c_naturales AS FLOAT)) as prom_ciencias,
                   AVG(CAST(punt_sociales_ciudadanas AS FLOAT)) as prom_sociales
            FROM socioeconomico.icfes_raw
            WHERE {where}
            GROUP BY cole_nombre_establecimiento, periodo
            ORDER BY periodo DESC, prom_global DESC
        """
    with engine.connect() as conn:
        rows = conn.execute(text(sql), params).fetchall()
        columns = conn.execute(text(sql), params).keys()
    return [dict(zip(columns, row)) for row in rows]


@router.get("/seguridad/serie")
def get_seguridad_serie(
    tipo: str = Query("homicidios", description="homicidios, hurtos, delitos_sexuales, violencia_intrafamiliar"),
):
    """Serie temporal de delitos por año."""
    table_map = {
        "homicidios": "seguridad.homicidios_raw",
        "hurtos": "seguridad.hurtos_raw",
        "delitos_sexuales": "seguridad.delitos_sexuales_raw",
        "violencia_intrafamiliar": "seguridad.violencia_intrafamiliar_raw",
    }
    table = table_map.get(tipo)
    if not table:
        return {"error": f"Tipo '{tipo}' no válido. Opciones: {list(table_map.keys())}"}

    sql = f"""
        SELECT EXTRACT(YEAR FROM fecha_hecho)::int as anio,
               SUM(CAST(cantidad AS INT)) as total,
               sexo,
               COUNT(*) as registros
        FROM {table}
        WHERE fecha_hecho IS NOT NULL
        GROUP BY anio, sexo
        ORDER BY anio, sexo
    """
    with engine.connect() as conn:
        rows = conn.execute(text(sql)).fetchall()
    return [{"anio": r[0], "total": r[1], "sexo": r[2], "registros": r[3]} for r in rows]


@router.get("/seguridad/resumen")
def get_seguridad_resumen():
    """Resumen de todos los indicadores de seguridad."""
    tables = {
        "homicidios": "seguridad.homicidios_raw",
        "hurtos": "seguridad.hurtos_raw",
        "delitos_sexuales": "seguridad.delitos_sexuales_raw",
        "violencia_intrafamiliar": "seguridad.violencia_intrafamiliar_raw",
    }
    result = {}
    with engine.connect() as conn:
        for name, table in tables.items():
            row = conn.execute(text(f"""
                SELECT COUNT(*) as registros,
                       SUM(CAST(cantidad AS INT)) as total_casos,
                       MIN(fecha_hecho) as desde,
                       MAX(fecha_hecho) as hasta
                FROM {table}
            """)).fetchone()
            result[name] = {
                "registros": row[0],
                "total_casos": row[1],
                "desde": str(row[2]) if row[2] else None,
                "hasta": str(row[3]) if row[3] else None,
            }
    return result


@router.get("/victimas")
def get_victimas(
    hecho: str = Query(None, description="Tipo de hecho victimizante"),
    aggregate: str = Query("hecho", description="hecho, sexo, etnia, ciclo_vital"),
):
    """Víctimas del conflicto armado con múltiples dimensiones."""
    group_col = {
        "hecho": "hecho",
        "sexo": "sexo",
        "etnia": "etnia",
        "ciclo_vital": "ciclo_vital",
    }.get(aggregate, "hecho")

    conditions = ["1=1"]
    params = {}
    if hecho:
        conditions.append("hecho = :h")
        params["h"] = hecho

    where = " AND ".join(conditions)
    sql = f"""
        SELECT {group_col} as dimension,
               SUM(CAST(per_ocu AS INT)) as personas,
               SUM(CAST(eventos AS INT)) as eventos,
               COUNT(*) as registros
        FROM seguridad.victimas_raw
        WHERE {where}
        GROUP BY {group_col}
        ORDER BY personas DESC
    """
    with engine.connect() as conn:
        rows = conn.execute(text(sql), params).fetchall()
    return [{"dimension": r[0], "personas": r[1], "eventos": r[2], "registros": r[3]} for r in rows]


@router.get("/educacion/establecimientos")
def get_establecimientos(
    sector: str = Query(None, description="OFICIAL o NO OFICIAL"),
):
    """Establecimientos educativos con matrícula."""
    conditions = ["1=1"]
    params = {}
    if sector:
        conditions.append("sector = :s")
        params["s"] = sector
    where = " AND ".join(conditions)
    sql = f"""
        SELECT nombre_establecimiento, codigo_dane, municipio, sector, caracter,
               calendario, direccion, total_matricula, cantidad_sedes
        FROM socioeconomico.establecimientos_educativos_raw
        WHERE {where}
        ORDER BY CAST(total_matricula AS INT) DESC NULLS LAST
    """
    with engine.connect() as conn:
        rows = conn.execute(text(sql), params).fetchall()
        cols = conn.execute(text(sql), params).keys()
    return [dict(zip(cols, r)) for r in rows]


@router.get("/salud/ips")
def get_ips():
    """Instituciones Prestadoras de Servicios de Salud."""
    sql = """
        SELECT nombreprestador, nombresede, naturalezajuridica, ese,
               municipioprestadordesc, departamentoprestadordesc,
               direccionprestador, telefonoprestador
        FROM socioeconomico.ips_raw
        LIMIT 500
    """
    with engine.connect() as conn:
        rows = conn.execute(text(sql)).fetchall()
        cols = conn.execute(text(sql)).keys()
    return [dict(zip(cols, r)) for r in rows]


# ── Sprint 3 endpoints ──────────────────────────────────────────────


@router.get("/terridata")
def get_terridata(
    dimension: str = Query(None, description="Dimension (Salud, Economía, Finanzas públicas, etc.)"),
    indicador: str = Query(None, description="Filtrar por nombre de indicador (parcial, ILIKE)"),
):
    """Indicadores TerriData DNP por dimensión."""
    conditions = ["1=1"]
    params = {}
    if dimension:
        conditions.append("dimension = :d")
        params["d"] = dimension
    if indicador:
        conditions.append("indicador ILIKE :i")
        params["i"] = f"%{indicador}%"
    where = " AND ".join(conditions)
    sql = f"""
        SELECT dimension, subcategoria, indicador,
               dato_numerico, dato_cualitativo, anio,
               fuente, unidad_de_medida
        FROM socioeconomico.terridata
        WHERE {where}
        ORDER BY dimension, indicador, anio
    """
    with engine.connect() as conn:
        rows = conn.execute(text(sql), params).fetchall()
        cols = conn.execute(text(sql), params).keys()
    return [dict(zip(cols, r)) for r in rows]


@router.get("/salud/irca")
def get_irca():
    """Indice de Riesgo de la Calidad del Agua (IRCA) por año."""
    sql = """
        SELECT a_o::int as anio,
               CASE WHEN irca ~ '^[0-9.]+$' THEN irca::float ELSE NULL END as irca_total,
               nivel_de_riesgo,
               CASE WHEN ircaurbano ~ '^[0-9.]+$' THEN ircaurbano::float ELSE NULL END as irca_urbano,
               nivel_de_riesgo_urbano,
               CASE WHEN ircarural ~ '^[0-9.]+$' THEN ircarural::float ELSE NULL END as irca_rural,
               nivel_de_riesgo_rural
        FROM socioeconomico.irca_raw
        ORDER BY a_o::int
    """
    with engine.connect() as conn:
        rows = conn.execute(text(sql)).fetchall()
        cols = conn.execute(text(sql)).keys()
    return [dict(zip(cols, r)) for r in rows]


@router.get("/salud/sivigila")
def get_sivigila(
    anio: int = Query(None, description="Filtrar por año"),
):
    """Eventos epidemiologicos SIVIGILA agregados."""
    conditions = ["1=1"]
    params = {}
    if anio:
        conditions.append("ano::int = :a")
        params["a"] = anio
    where = " AND ".join(conditions)
    sql = f"""
        SELECT nombre as evento,
               ano::int as anio,
               SUM(conteo_casos::int) as casos
        FROM socioeconomico.sivigila_raw
        WHERE {where}
        GROUP BY nombre, ano
        ORDER BY ano, casos DESC
    """
    with engine.connect() as conn:
        rows = conn.execute(text(sql), params).fetchall()
        cols = conn.execute(text(sql)).keys()
    results = [dict(zip(cols, r)) for r in rows]
    return results


@router.get("/salud/sivigila/resumen")
def get_sivigila_resumen():
    """Top eventos epidemiologicos SIVIGILA todos los años."""
    sql = """
        SELECT nombre as evento,
               SUM(conteo_casos::int) as total_casos,
               COUNT(DISTINCT ano) as anios
        FROM socioeconomico.sivigila_raw
        GROUP BY nombre
        ORDER BY total_casos DESC
    """
    with engine.connect() as conn:
        rows = conn.execute(text(sql)).fetchall()
        cols = conn.execute(text(sql)).keys()
    return [dict(zip(cols, r)) for r in rows]


@router.get("/economia/internet")
def get_internet():
    """Accesos a Internet Fijo por año y segmento."""
    sql = """
        SELECT anno::int as anio,
               segmento,
               SUM(no_de_accesos::int) as accesos,
               COUNT(DISTINCT proveedor) as proveedores
        FROM servicios.internet_fijo_raw
        WHERE no_de_accesos ~ '^[0-9]+'
        GROUP BY anno, segmento
        ORDER BY anno, accesos DESC
    """
    with engine.connect() as conn:
        rows = conn.execute(text(sql)).fetchall()
        cols = conn.execute(text(sql)).keys()
    return [dict(zip(cols, r)) for r in rows]


@router.get("/economia/internet/serie")
def get_internet_serie():
    """Serie anual total de accesos a Internet Fijo."""
    sql = """
        SELECT anno::int as anio,
               SUM(no_de_accesos::int) as total_accesos,
               COUNT(DISTINCT proveedor) as proveedores,
               COUNT(DISTINCT segmento) as segmentos
        FROM servicios.internet_fijo_raw
        WHERE no_de_accesos ~ '^[0-9]+'
        GROUP BY anno
        ORDER BY anno
    """
    with engine.connect() as conn:
        rows = conn.execute(text(sql)).fetchall()
        cols = conn.execute(text(sql)).keys()
    return [dict(zip(cols, r)) for r in rows]


@router.get("/economia/secop")
def get_secop_resumen():
    """Resumen de contratacion publica SECOP."""
    sql = """
        SELECT tipo_de_contrato,
               COUNT(*) as contratos,
               SUM(CASE WHEN valor_contrato ~ '^[0-9.]+$'
                   THEN valor_contrato::numeric ELSE 0 END) as valor_total,
               AVG(CASE WHEN valor_contrato ~ '^[0-9.]+$'
                   THEN valor_contrato::numeric ELSE NULL END) as valor_promedio
        FROM servicios.secop_raw
        GROUP BY tipo_de_contrato
        ORDER BY contratos DESC
    """
    with engine.connect() as conn:
        rows = conn.execute(text(sql)).fetchall()
        cols = conn.execute(text(sql)).keys()
    return [dict(zip(cols, r)) for r in rows]


@router.get("/economia/turismo")
def get_turismo():
    """Establecimientos turisticos RNT."""
    sql = """
        SELECT COUNT(*) as total,
               COUNT(DISTINCT categoria) as categorias
        FROM servicios.rnt_turismo_raw
    """
    with engine.connect() as conn:
        total_row = conn.execute(text(sql)).fetchone()

    sql2 = """
        SELECT categoria, COUNT(*) as establecimientos
        FROM servicios.rnt_turismo_raw
        WHERE categoria IS NOT NULL
        GROUP BY categoria
        ORDER BY establecimientos DESC
    """
    with engine.connect() as conn:
        rows = conn.execute(text(sql2)).fetchall()
    return {
        "total": total_row[0],
        "categorias": total_row[1],
        "detalle": [{"categoria": r[0], "establecimientos": r[1]} for r in rows],
    }


@router.get("/economia/agricola")
def get_agricola():
    """Evaluaciones agropecuarias EVA."""
    sql = """
        SELECT * FROM socioeconomico.eva_agricola_raw
        ORDER BY 1
        LIMIT 200
    """
    with engine.connect() as conn:
        rows = conn.execute(text(sql)).fetchall()
        cols = conn.execute(text(sql)).keys()
    return [dict(zip(cols, r)) for r in rows]


@router.get("/gobierno/finanzas")
def get_finanzas():
    """Indicadores de finanzas publicas de TerriData."""
    key_indicators = [
        'Ingresos totales', 'Gastos totales',
        'Ingresos tributarios', 'Gastos corrientes',
        'Gastos de capital (Inversión)',
        'Indicador de desempeño fiscal',
        'Ingresos totales per cápita', 'Gastos totales per cápita',
        'Capacidad de ahorro', 'Dependencia de las transferencias',
    ]
    placeholders = ", ".join([f":p{i}" for i in range(len(key_indicators))])
    params = {f"p{i}": v for i, v in enumerate(key_indicators)}
    sql = f"""
        SELECT indicador, dato_numerico, anio, unidad_de_medida, fuente
        FROM socioeconomico.terridata
        WHERE dimension = 'Finanzas públicas'
          AND indicador IN ({placeholders})
        ORDER BY indicador, anio
    """
    with engine.connect() as conn:
        rows = conn.execute(text(sql), params).fetchall()
        cols = conn.execute(text(sql), params).keys()
    return [dict(zip(cols, r)) for r in rows]


@router.get("/gobierno/desempeno")
def get_desempeno():
    """Medicion de Desempeno Municipal (MDM) de TerriData."""
    sql = """
        SELECT indicador, dato_numerico, dato_cualitativo, anio,
               unidad_de_medida, fuente
        FROM socioeconomico.terridata
        WHERE dimension = 'Medición de desempeño municipal'
        ORDER BY indicador, anio
    """
    with engine.connect() as conn:
        rows = conn.execute(text(sql)).fetchall()
        cols = conn.execute(text(sql)).keys()
    return [dict(zip(cols, r)) for r in rows]


@router.get("/gobierno/digital")
def get_gobierno_digital():
    """Indice de Gobierno Digital."""
    sql = """
        SELECT vigencia::int as anio, ndice as indice,
               puntaje_entidad::float as puntaje,
               promedio_grupo_par::float as promedio_grupo,
               m_ximo_grupo_par::float as max_grupo,
               m_nimo_grupo_par::float as min_grupo,
               quintil_grupo_par as quintil,
               percentil_grupo_par as percentil
        FROM socioeconomico.gobierno_digital_raw
        ORDER BY vigencia, ndice
    """
    with engine.connect() as conn:
        rows = conn.execute(text(sql)).fetchall()
        cols = conn.execute(text(sql)).keys()
    return [dict(zip(cols, r)) for r in rows]


@router.get("/gobierno/pobreza")
def get_pobreza():
    """Indicadores de pobreza (IPM, NBI) de TerriData."""
    sql = """
        SELECT indicador, dato_numerico, anio, unidad_de_medida, fuente
        FROM socioeconomico.terridata
        WHERE dimension = 'Pobreza'
        ORDER BY indicador, anio
    """
    with engine.connect() as conn:
        rows = conn.execute(text(sql)).fetchall()
        cols = conn.execute(text(sql)).keys()
    results = [dict(zip(cols, r)) for r in rows]

    ipm_sql = """
        SELECT * FROM socioeconomico.ipm_raw LIMIT 30
    """
    with engine.connect() as conn:
        ipm_rows = conn.execute(text(ipm_sql)).fetchall()
        ipm_cols = conn.execute(text(ipm_sql)).keys()
    ipm = [dict(zip(ipm_cols, r)) for r in ipm_rows]

    return {"terridata": results, "ipm_detalle": ipm}
