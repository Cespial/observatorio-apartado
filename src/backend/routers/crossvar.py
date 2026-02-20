"""
Motor de Cruces Multivariable
"""
import logging
from fastapi import APIRouter, Query
from ..database import engine, cached, query_dicts
from sqlalchemy import text

logger = logging.getLogger("observatorio.crossvar")

router = APIRouter(prefix="/api/crossvar", tags=["Cruces Multivariable"])

VARIABLES = {
    "poblacion": {"name": "Población total", "source": "terridata", "indicador": "Población total"},
    "icfes": {"name": "Puntaje ICFES", "source": "terridata", "indicador": "Puntaje promedio Pruebas Saber 11 - Matemáticas"},
    "homicidios": {"name": "Tasa de homicidios", "source": "terridata", "indicador": "Tasa de homicidios por cada 100.000 habitantes"},
    "hurtos": {"name": "Tasa de hurtos", "source": "terridata", "indicador": "Tasa de hurto común por cada 100.000 habitantes"},
    "pobreza": {"name": "Pobreza multidimensional (IPM)", "source": "terridata", "indicador": "Índice de pobreza multidimensional - IPM"},
    "valor_agregado": {"name": "Valor agregado per cápita", "source": "terridata", "indicador": "Valor agregado per cápita"},
    "desercion": {"name": "Tasa de deserción escolar", "source": "terridata", "indicador": "Tasa de deserción intra-anual del sector oficial en educación básica y media (Desde transición hasta once)"},
    "vif": {"name": "Violencia intrafamiliar", "source": "terridata", "indicador": "Tasa de violencia intrafamiliar por cada 100.000 habitantes"},
}


@router.get("/variables")
def list_variables():
    return [{"id": k, "name": v["name"]} for k, v in VARIABLES.items()]


@router.get("/security-matrix")
@cached(ttl_seconds=600)
def security_matrix(dane_code: str = Query(None)):
    where = "WHERE dane_code = :d" if dane_code else "WHERE 1=1"
    parts = []
    for label, table in [
        ("Homicidios", "seguridad.homicidios"),
        ("Hurtos", "seguridad.hurtos"),
        ("Violencia Intrafamiliar", "seguridad.violencia_intrafamiliar"),
        ("Delitos Sexuales", "seguridad.delitos_sexuales"),
    ]:
        parts.append(
            f"SELECT '{label}' as tipo, EXTRACT(YEAR FROM fecha)::int as anio, "
            f"SUM(cantidad) as total FROM {table} {where} GROUP BY anio"
        )
    sql = " UNION ALL ".join(parts) + " ORDER BY tipo, anio"
    try:
        return {"data": query_dicts(sql, {"d": dane_code})}
    except Exception as e:
        logger.warning("security_matrix error: %s", e)
        return {"data": []}


@router.get("/scatter")
@cached(ttl_seconds=600)
def scatter_analysis(var_x: str, var_y: str, dane_code: str = Query(None)):
    """Scatter plot: compares two TerriData indicators across municipalities."""
    vx = VARIABLES.get(var_x)
    vy = VARIABLES.get(var_y)
    if not vx or not vy:
        return {"points": [], "correlation": 0, "n": 0, "error": "Variable no encontrada"}

    sql = """
        WITH x_data AS (
            SELECT DISTINCT ON (entidad)
                entidad as municipio, codigo_entidad as dane_code,
                dato_numerico as valor, anio
            FROM socioeconomico.terridata
            WHERE indicador = :ind_x
            ORDER BY entidad, anio DESC
        ),
        y_data AS (
            SELECT DISTINCT ON (entidad)
                entidad as municipio, codigo_entidad as dane_code,
                dato_numerico as valor, anio
            FROM socioeconomico.terridata
            WHERE indicador = :ind_y
            ORDER BY entidad, anio DESC
        )
        SELECT x.municipio as label, x.valor as x, y.valor as y
        FROM x_data x
        JOIN y_data y ON x.dane_code = y.dane_code
        WHERE x.valor IS NOT NULL AND y.valor IS NOT NULL
    """
    try:
        points = query_dicts(sql, {"ind_x": vx["indicador"], "ind_y": vy["indicador"]})
        n = len(points)
        # Compute correlation
        correlation = 0.0
        if n > 2:
            xs = [p["x"] for p in points]
            ys = [p["y"] for p in points]
            mean_x = sum(xs) / n
            mean_y = sum(ys) / n
            cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / n
            std_x = (sum((x - mean_x) ** 2 for x in xs) / n) ** 0.5
            std_y = (sum((y - mean_y) ** 2 for y in ys) / n) ** 0.5
            if std_x > 0 and std_y > 0:
                correlation = round(cov / (std_x * std_y), 3)

        return {
            "var_x": {"name": vx["name"]},
            "var_y": {"name": vy["name"]},
            "points": points,
            "correlation": correlation,
            "regression": {"r_squared": round(correlation ** 2, 3)},
            "n": n,
        }
    except Exception as e:
        logger.warning("scatter error: %s", e)
        return {"points": [], "correlation": 0, "n": 0}
