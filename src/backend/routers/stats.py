"""
Resumen ejecutivo del municipio — dashboard summary
"""
from fastapi import APIRouter
from ..database import engine, cached
from sqlalchemy import text

from fastapi import Query

router = APIRouter(prefix="/api/stats", tags=["Resumen"])

MUNICIPIOS = {
    "05045": "Apartadó",
    "05837": "Turbo",
    "05147": "Carepa",
    "05172": "Chigorodó",
    "05490": "Necoclí",
    "05480": "Mutatá",
}

@router.get("/summary")
@cached(ttl_seconds=600)
def get_summary(
    dane_code: str = Query(None, description="Filtrar por código DANE del municipio")
):
    """
    Resumen ejecutivo regional o por municipio.
    """
    stats = {
        "region": "Urabá",
        "municipio": MUNICIPIOS.get(dane_code, "Toda la Región"),
        "dane_code": dane_code,
    }

    where_manzanas = "WHERE cod_dane_municipio = :dane" if dane_code else ""
    where_terridata = "WHERE codigo_municipio = :dane" if dane_code else ""
    where_icfes = "WHERE cole_cod_mcpio_ubicacion = :dane" if dane_code else ""
    where_seguridad = "WHERE codigo_dane = :dane" if dane_code else ""
    where_edu = "WHERE codigo_dane LIKE :dane_prefix" if dane_code else ""
    
    params = {"dane": dane_code, "dane_prefix": f"{dane_code}%"} if dane_code else {}

    with engine.connect() as conn:
        # Población (TerriData)
        pop_sql = f"SELECT SUM(dato_numerico::int), anio FROM socioeconomico.terridata {where_terridata} {'AND' if dane_code else 'WHERE'} indicador = 'Población total' GROUP BY anio ORDER BY anio DESC LIMIT 1"
        pop_row = conn.execute(text(pop_sql), params).fetchone()
        stats["poblacion_total"] = pop_row[0] if pop_row else None
        stats["poblacion_anio"] = pop_row[1] if pop_row else None

        stats["manzanas_censales"] = conn.execute(text(
            f"SELECT COUNT(*) FROM cartografia.manzanas_censales {where_manzanas}"
        ), params).scalar()

        # ICFES
        icfes_sql = f"""
            SELECT COUNT(DISTINCT cole_nombre_establecimiento) as colegios,
                   COUNT(*) as estudiantes_evaluados,
                   AVG(CAST(punt_global AS FLOAT)) as prom_global
            FROM socioeconomico.icfes_raw
            {where_icfes} {'AND' if dane_code else 'WHERE'} punt_global IS NOT NULL
        """
        icfes = conn.execute(text(icfes_sql), params).fetchone()
        stats["icfes"] = {
            "colegios_evaluados": icfes[0],
            "estudiantes_evaluados": icfes[1],
            "promedio_global": round(float(icfes[2]), 1) if icfes[2] else None,
        }

        # Seguridad (Agregado)
        seguridad = {}
        for table, key in [
            ("homicidios_raw", "total_homicidios"),
            ("hurtos_raw", "total_hurtos"),
            ("delitos_sexuales_raw", "total_delitos_sexuales"),
            ("violencia_intrafamiliar_raw", "total_vif"),
        ]:
            val = conn.execute(text(
                f"SELECT SUM(CAST(cantidad AS INT)) FROM seguridad.{table} {where_seguridad}"
            ), params).scalar()
            seguridad[key] = int(val) if val else 0
        stats["seguridad"] = seguridad

    return stats


@router.get("/catalog-summary")
@cached(ttl_seconds=3600)
def get_catalog_summary():
    """Resumen ligero del catálogo: total de tablas y registros."""
    sql = """
        SELECT COUNT(*) AS tables,
               SUM(cnt) AS records
        FROM (
            SELECT schemaname, tablename,
                   (xpath('/row/cnt/text()',
                     xml_content))[1]::text::bigint AS cnt
            FROM (
                SELECT schemaname, tablename,
                       query_to_xml(
                         format('SELECT COUNT(*) AS cnt FROM %I.%I', schemaname, tablename),
                         false, true, ''
                       ) AS xml_content
                FROM pg_tables
                WHERE schemaname IN ('cartografia','socioeconomico','seguridad','servicios','catastro')
            ) sub
        ) counts
    """
    with engine.connect() as conn:
        row = conn.execute(text(sql)).fetchone()
    return {
        "tables": row[0] if row else 0,
        "records": row[1] if row else 0,
    }


@router.get("/data-catalog")
@cached(ttl_seconds=3600)
def get_data_catalog():
    """Catálogo completo de datos disponibles en la plataforma."""
    catalog = []
    tables_query = """
        SELECT schemaname, tablename
        FROM pg_tables
        WHERE schemaname IN ('cartografia', 'socioeconomico', 'seguridad', 'servicios', 'catastro')
        ORDER BY schemaname, tablename
    """
    with engine.connect() as conn:
        tables = conn.execute(text(tables_query)).fetchall()
        for schema, table in tables:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {schema}.{table}")).scalar()
            cols = conn.execute(text(
                "SELECT column_name, data_type FROM information_schema.columns "
                "WHERE table_schema = :s AND table_name = :t ORDER BY ordinal_position"
            ), {"s": schema, "t": table}).fetchall()
            catalog.append({
                "schema": schema,
                "table": table,
                "full_name": f"{schema}.{table}",
                "records": count,
                "columns": [{"name": c[0], "type": c[1]} for c in cols],
            })
    return catalog
