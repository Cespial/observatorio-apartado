"""
Resumen ejecutivo regional y por municipio
"""
import logging
from fastapi import APIRouter, Query
from ..database import engine, cached, query_dicts
from sqlalchemy import text

logger = logging.getLogger("observatorio.stats")

router = APIRouter(prefix="/api/stats", tags=["Resumen"])

MUNICIPIOS = {
    "05045": "Apartadó", "05837": "Turbo", "05147": "Carepa", "05172": "Chigorodó",
    "05490": "Necoclí", "05051": "Arboletes", "05665": "San Pedro de Urabá",
    "05659": "San Juan de Urabá", "05480": "Mutatá", "05475": "Murindó",
    "05873": "Vigía del Fuerte"
}


def _safe_scalar(conn, sql, params, default=0):
    """Execute a scalar query, returning default on error."""
    try:
        val = conn.execute(text(sql), params).scalar()
        return int(val) if val else default
    except Exception as e:
        logger.warning("Query failed: %s — %s", sql[:80], e)
        return default


def _safe_row(conn, sql, params):
    """Execute and return first row, or None on error."""
    try:
        return conn.execute(text(sql), params).fetchone()
    except Exception as e:
        logger.warning("Query failed: %s — %s", sql[:80], e)
        return None


def _terridata_value(conn, indicador, params, where):
    """Get latest numeric value from TerriData for a given indicator."""
    sql = f"SELECT dato_numerico, anio FROM socioeconomico.terridata {where} AND indicador = :ind ORDER BY anio DESC LIMIT 1"
    row = _safe_row(conn, sql, {**params, "ind": indicador})
    return (row[0], row[1]) if row and row[0] is not None else (None, None)


@router.get("/summary")
@cached(ttl_seconds=600)
def get_summary(dane_code: str = Query(None)):
    dane = dane_code.zfill(5) if dane_code and dane_code.isdigit() else dane_code

    stats = {
        "region": "Urabá",
        "municipio": MUNICIPIOS.get(dane, "Toda la Región"),
        "departamento": "Antioquia",
        "divipola": dane or "REGIONAL",
    }

    params = {"dane": dane} if dane else {}
    where = "WHERE dane_code = :dane" if dane else "WHERE 1=1"

    with engine.connect() as conn:
        # 1. Población total (TerriData)
        pop, pop_year = _terridata_value(conn, "Población total", params, where)
        stats["poblacion_total"] = int(pop) if pop else None
        stats["poblacion_anio"] = pop_year

        # 2. Manzanas censales
        stats["manzanas_censales"] = _safe_scalar(
            conn, f"SELECT COUNT(*) FROM cartografia.manzanas_censales WHERE cod_dane_municipio = :dane",
            params) if dane else _safe_scalar(
            conn, "SELECT COUNT(*) FROM cartografia.manzanas_censales", {})

        # 3. Establecimientos comerciales (Google Places)
        stats["establecimientos_comerciales"] = _safe_scalar(
            conn, f"SELECT COUNT(*) FROM servicios.google_places_regional {where}", params)

        # 4. Establecimientos educativos
        val = _safe_scalar(conn, f"SELECT COUNT(*) FROM socioeconomico.establecimientos_educativos {where}", params)
        if not val:
            # Fallback: TerriData "Número de sedes educativas" or similar
            td_val, _ = _terridata_value(conn, "Número de sedes educativas en el sector oficial", params, where)
            val = int(td_val) if td_val else 0
        stats["establecimientos_educativos"] = val

        # 5. Matrícula total
        val = _safe_scalar(
            conn, f"SELECT SUM(total_matricula) FROM socioeconomico.establecimientos_educativos {where}", params)
        if not val:
            td_val, _ = _terridata_value(conn, "Cobertura neta en educación", params, where)
            stats["matricula_total"] = int(td_val) if td_val else 0
        else:
            stats["matricula_total"] = val

        # 6. IPS de salud
        stats["ips_salud"] = _safe_scalar(
            conn, f"SELECT COUNT(*) FROM socioeconomico.ips_salud {where}", params)

        # 7. Prestadores de servicios
        stats["prestadores_servicios"] = _safe_scalar(
            conn, f"SELECT COUNT(*) FROM socioeconomico.prestadores_servicios {where}", params)

        # 8. Homicidios (tabla seguridad → fallback TerriData tasa)
        h_val = _safe_scalar(conn, f"SELECT SUM(cantidad) FROM seguridad.homicidios {where}", params, default=None)
        if not h_val:
            td_val, _ = _terridata_value(conn, "Tasa de homicidios por cada 100.000 habitantes", params, where)
            if td_val and pop:
                h_val = int(td_val * pop / 100000)
            else:
                h_val = 0
        stats["total_homicidios"] = h_val

        # 9. Hurtos (tabla seguridad → fallback TerriData tasa)
        hu_val = _safe_scalar(conn, f"SELECT SUM(cantidad) FROM seguridad.hurtos {where}", params, default=None)
        if not hu_val:
            td_val, _ = _terridata_value(conn, "Tasa de hurto común por cada 100.000 habitantes", params, where)
            if td_val and pop:
                hu_val = int(td_val * pop / 100000)
            else:
                hu_val = 0
        stats["total_hurtos"] = hu_val

        # 10. Violencia intrafamiliar
        vif_val = _safe_scalar(conn, f"SELECT SUM(cantidad) FROM seguridad.violencia_intrafamiliar {where}", params, default=None)
        if not vif_val:
            td_val, _ = _terridata_value(conn, "Tasa de violencia intrafamiliar por cada 100.000 habitantes", params, where)
            if td_val and pop:
                vif_val = int(td_val * pop / 100000)
            else:
                vif_val = 0
        stats["total_vif"] = vif_val

        # 11. Víctimas del conflicto
        stats["total_victimas_conflicto"] = _safe_scalar(
            conn, f"SELECT SUM(personas) FROM seguridad.victimas_conflicto {where}", params)

        # 12. ICFES promedio
        icfes_row = _safe_row(
            conn, f"SELECT AVG(punt_global) FROM socioeconomico.icfes {where}", params)
        icfes_avg = round(icfes_row[0], 1) if icfes_row and icfes_row[0] else None
        if not icfes_avg:
            # Fallback: TerriData Saber 11 scores
            td_mat, _ = _terridata_value(conn, "Puntaje promedio Pruebas Saber 11 - Matemáticas", params, where)
            td_lec, _ = _terridata_value(conn, "Puntaje promedio Pruebas Saber 11 - Lectura crítica", params, where)
            if td_mat and td_lec:
                icfes_avg = round((td_mat + td_lec) / 2, 1)
        stats["icfes"] = {"promedio_global": icfes_avg} if icfes_avg else None

        # 13. Principales hechos victimizantes
        try:
            hechos = conn.execute(text(f"""
                SELECT hecho, SUM(personas) as personas
                FROM seguridad.victimas_conflicto {where}
                GROUP BY hecho ORDER BY personas DESC LIMIT 5
            """), params).fetchall()
            stats["principales_hechos_victimizantes"] = [
                {"hecho": h[0], "personas": int(h[1])} for h in hechos
            ] if hechos else []
        except Exception:
            stats["principales_hechos_victimizantes"] = []

    return stats

@router.get("/catalog-summary")
@cached(ttl_seconds=3600)
def get_catalog_summary():
    try:
        with engine.connect() as conn:
            # Safer query for record count
            sql = """
                SELECT COUNT(*) as tables, 
                       COALESCE(SUM(n_live_tup), 0) as records 
                FROM pg_stat_user_tables 
                WHERE schemaname IN ('cartografia','socioeconomico','seguridad','servicios','catastro')
            """
            row = conn.execute(text(sql)).fetchone()
            return {"tables": row[0] or 0, "records": int(row[1]) if row and row[1] else 0}
    except Exception as e: 
        print(f"Catalog summary error: {e}")
        return {"tables": 0, "records": 0}
