"""
Endpoints de indicadores socioeconómicos, educativos, salud, economía y seguridad
"""
from fastapi import APIRouter, Query
from ..database import query_dicts

router = APIRouter(prefix="/api/indicators", tags=["Indicadores"])

TABLES = {
    "icfes": "socioeconomico.icfes",
    "homicidios": "seguridad.homicidios",
    "hurtos": "seguridad.hurtos",
    "vif": "seguridad.violencia_intrafamiliar",
    "delitos_sexuales": "seguridad.delitos_sexuales",
    "victimas": "seguridad.victimas_conflicto",
    "terridata": "socioeconomico.terridata",
    "ips": "socioeconomico.ips_salud",
    "establecimientos": "socioeconomico.establecimientos_educativos",
    "places": "servicios.google_places_regional"
}

@router.get("/icfes")
def get_icfes(dane_code: str = Query(None), aggregate: str = Query("colegio")):
    cond = ["1=1"]
    if dane_code: cond.append("dane_code = :dane")
    where = " AND ".join(cond)
    if aggregate == "periodo":
        sql = f"SELECT periodo, COUNT(*) as estudiantes, AVG(punt_global) as prom_global FROM {TABLES['icfes']} WHERE {where} GROUP BY periodo ORDER BY periodo"
    else:
        sql = f"SELECT cole_nombre as colegio, periodo, AVG(punt_global) as prom_global FROM {TABLES['icfes']} WHERE {where} GROUP BY cole_nombre, periodo ORDER BY prom_global DESC"
    return query_dicts(sql, {"dane": dane_code})

@router.get("/terridata")
def get_terridata(dane_code: str = Query(None), dimension: str = Query(None)):
    cond = ["1=1"]
    if dane_code: cond.append("dane_code = :dane")
    if dimension: cond.append("dimension = :dim")
    sql = f"SELECT dimension, indicador, dato_numerico, anio, unidad_de_medida FROM {TABLES['terridata']} WHERE {' AND '.join(cond)} ORDER BY anio DESC"
    return query_dicts(sql, {"dane": dane_code, "dim": dimension})

@router.get("/seguridad/serie")
def get_seguridad_serie(tipo: str = "homicidios", dane_code: str = Query(None)):
    table = TABLES.get(tipo, TABLES["homicidios"])
    cond = ["1=1"]
    if dane_code: cond.append("dane_code = :dane")
    sql = f"SELECT EXTRACT(YEAR FROM fecha)::int as anio, SUM(cantidad) as total FROM {table} WHERE {' AND '.join(cond)} GROUP BY anio ORDER BY anio"
    return query_dicts(sql, {"dane": dane_code})

@router.get("/victimas")
def get_victimas(dane_code: str = Query(None), aggregate: str = Query("hecho")):
    cond = ["1=1"]
    if dane_code: cond.append("dane_code = :dane")
    where = " AND ".join(cond)
    if aggregate == "hecho":
        sql = f"SELECT hecho as dimension, SUM(personas) as personas FROM {TABLES['victimas']} WHERE {where} GROUP BY hecho ORDER BY personas DESC"
    else:
        sql = f"SELECT sexo, hecho, SUM(personas) as personas FROM {TABLES['victimas']} WHERE {where} GROUP BY sexo, hecho ORDER BY personas DESC"
    return query_dicts(sql, {"dane": dane_code})

@router.get("/salud/ips")
def get_ips(dane_code: str = Query(None)):
    cond = ["1=1"]
    if dane_code: cond.append("dane_code = :dane")
    sql = f"SELECT nombre, clase_persona, direccion, telefono FROM {TABLES['ips']} WHERE {' AND '.join(cond)} LIMIT 200"
    return query_dicts(sql, {"dane": dane_code})

@router.get("/salud/irca")
def get_irca(dane_code: str = Query(None)):
    """IRCA (Indice de Riesgo de Calidad de Agua) from TerriData."""
    cond = ["indicador ILIKE '%IRCA%'"]
    params = {}
    if dane_code:
        cond.append("dane_code = :d")
        params["d"] = dane_code
    sql = f"SELECT anio, dato_numerico as irca_total, entidad as municipio FROM {TABLES['terridata']} WHERE {' AND '.join(cond)} ORDER BY anio"
    return query_dicts(sql, params)

@router.get("/salud/sivigila/resumen")
def get_sivigila_resumen(dane_code: str = Query(None)):
    """Sivigila data from TerriData health indicators."""
    cond = ["dimension = 'Salud'"]
    params = {}
    if dane_code:
        cond.append("dane_code = :d")
        params["d"] = dane_code
    sql = f"SELECT indicador, dato_numerico as valor, anio, entidad as municipio FROM {TABLES['terridata']} WHERE {' AND '.join(cond)} ORDER BY anio DESC LIMIT 50"
    return query_dicts(sql, params)

@router.get("/economia/internet/serie")
def get_internet_serie(dane_code: str = Query(None)):
    cond = ["indicador ILIKE '%Internet%'"]
    params = {}
    if dane_code:
        cond.append("dane_code = :d")
        params["d"] = dane_code
    sql = f"SELECT anio, dato_numerico as total_accesos, entidad as municipio FROM {TABLES['terridata']} WHERE {' AND '.join(cond)} ORDER BY anio"
    return query_dicts(sql, params)

@router.get("/economia/secop")
def get_secop_resumen(dane_code: str = Query(None)):
    """Contratacion publica - proxy from TerriData fiscal indicators."""
    cond = ["dimension = 'Finanzas públicas'", "indicador ILIKE '%inversión%'"]
    params = {}
    if dane_code:
        cond.append("dane_code = :d")
        params["d"] = dane_code
    sql = f"SELECT indicador, dato_numerico as valor, anio, entidad as municipio FROM {TABLES['terridata']} WHERE {' AND '.join(cond)} ORDER BY anio DESC LIMIT 30"
    return query_dicts(sql, params)

@router.get("/economia/turismo")
def get_turismo(dane_code: str = Query(None)):
    """Turismo indicators from TerriData."""
    cond = ["indicador ILIKE '%turis%'"]
    params = {}
    if dane_code:
        cond.append("dane_code = :d")
        params["d"] = dane_code
    sql = f"SELECT indicador, dato_numerico as valor, anio, entidad as municipio FROM {TABLES['terridata']} WHERE {' AND '.join(cond)} ORDER BY anio DESC"
    data = query_dicts(sql, params)
    return {"total": len(data), "detalle": data}

@router.get("/gobierno/finanzas")
def get_finanzas(dane_code: str = Query(None)):
    return get_terridata(dane_code, "Finanzas públicas")

@router.get("/gobierno/desempeno")
def get_desempeno(dane_code: str = Query(None)):
    return get_terridata(dane_code, "Medición de desempeño municipal")

@router.get("/gobierno/digital")
def get_gobierno_digital(dane_code: str = Query(None)):
    """Gobierno digital indicators from TerriData."""
    cond = ["indicador ILIKE '%gobierno digital%' OR indicador ILIKE '%gobierno en línea%' OR indicador ILIKE '%TIC%'"]
    params = {}
    if dane_code:
        cond.append("dane_code = :d")
        params["d"] = dane_code
    sql = f"SELECT indicador, dato_numerico as valor, anio, entidad as municipio FROM {TABLES['terridata']} WHERE {' AND '.join(cond)} ORDER BY anio DESC LIMIT 30"
    return query_dicts(sql, params)

@router.get("/gobierno/pobreza")
def get_pobreza(dane_code: str = Query(None)):
    td = get_terridata(dane_code, "Pobreza")
    return {"terridata": td, "ipm_detalle": []}

@router.get("/cultura/espacios")
def get_espacios_culturales(dane_code: str = Query(None)):
    """Cultural spaces from TerriData or Google Places."""
    cond = ["indicador ILIKE '%cultur%' OR indicador ILIKE '%bibliotec%' OR indicador ILIKE '%museo%'"]
    params = {}
    if dane_code:
        cond.append("dane_code = :d")
        params["d"] = dane_code
    sql = f"SELECT indicador, dato_numerico as valor, anio, entidad as municipio FROM {TABLES['terridata']} WHERE {' AND '.join(cond)} ORDER BY anio DESC LIMIT 30"
    return query_dicts(sql, params)

@router.get("/cultura/turismo-detalle")
def get_turismo_detalle(dane_code: str = Query(None)):
    """Tourism detail from Google Places."""
    cond = ["category IN ('restaurant', 'hotel', 'lodging', 'tourist_attraction', 'travel_agency')"]
    params = {}
    if dane_code:
        cond.append("dane_code = :d")
        params["d"] = dane_code
    sql = f"SELECT category, COUNT(*) as total, AVG(rating) as avg_rating FROM {TABLES['places']} WHERE {' AND '.join(cond)} GROUP BY category ORDER BY total DESC"
    data = query_dicts(sql, params)
    return {"total": sum(d.get("total", 0) for d in data), "por_categoria": {d["category"]: d for d in data}}
