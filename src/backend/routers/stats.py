"""
Resumen ejecutivo del municipio — dashboard summary
"""
from fastapi import APIRouter
from ..database import engine
from sqlalchemy import text

router = APIRouter(prefix="/api/stats", tags=["Resumen"])


@router.get("/summary")
def get_summary():
    """
    Resumen ejecutivo de Apartadó — tarjetas principales del dashboard.
    """
    stats = {
        "municipio": "Apartadó",
        "divipola": "05045",
        "departamento": "Antioquia",
        "region": "Urabá",
    }

    with engine.connect() as conn:
        # Población (manzanas censales)
        pop = conn.execute(text(
            "SELECT SUM(CAST(total_personas AS INT)) FROM cartografia.manzanas_censales WHERE total_personas ~ '^[0-9]+$'"
        )).scalar()
        stats["poblacion_censal_2018"] = int(pop) if pop else None

        stats["manzanas_censales"] = conn.execute(text(
            "SELECT COUNT(*) FROM cartografia.manzanas_censales"
        )).scalar()

        # Edificaciones OSM
        stats["edificaciones_osm"] = conn.execute(text(
            "SELECT COUNT(*) FROM cartografia.osm_edificaciones"
        )).scalar()

        # Vías
        stats["vias_osm"] = conn.execute(text(
            "SELECT COUNT(*) FROM cartografia.osm_vias"
        )).scalar()

        # Google Places
        stats["establecimientos_comerciales"] = conn.execute(text(
            "SELECT COUNT(*) FROM servicios.google_places"
        )).scalar()

        # Establecimientos educativos
        stats["establecimientos_educativos"] = conn.execute(text(
            "SELECT COUNT(*) FROM socioeconomico.establecimientos_educativos_raw"
        )).scalar()

        # Matrícula total
        mat = conn.execute(text(
            "SELECT SUM(CAST(total_matricula AS INT)) FROM socioeconomico.establecimientos_educativos_raw WHERE total_matricula IS NOT NULL"
        )).scalar()
        stats["matricula_total"] = int(mat) if mat else None

        # ICFES
        icfes = conn.execute(text("""
            SELECT COUNT(DISTINCT cole_nombre_establecimiento) as colegios,
                   COUNT(*) as estudiantes_evaluados,
                   AVG(CAST(punt_global AS FLOAT)) as prom_global
            FROM socioeconomico.icfes_raw
            WHERE punt_global IS NOT NULL
        """)).fetchone()
        stats["icfes"] = {
            "colegios_evaluados": icfes[0],
            "estudiantes_evaluados": icfes[1],
            "promedio_global": round(float(icfes[2]), 1) if icfes[2] else None,
        }

        # IPS Salud
        stats["ips_salud"] = conn.execute(text(
            "SELECT COUNT(*) FROM socioeconomico.ips_raw"
        )).scalar()

        # Seguridad
        for table, key in [
            ("homicidios_raw", "total_homicidios"),
            ("hurtos_raw", "total_hurtos"),
            ("delitos_sexuales_raw", "total_delitos_sexuales"),
            ("violencia_intrafamiliar_raw", "total_vif"),
        ]:
            val = conn.execute(text(
                f"SELECT SUM(CAST(cantidad AS INT)) FROM seguridad.{table}"
            )).scalar()
            stats[key] = int(val) if val else 0

        # Víctimas conflicto
        vic = conn.execute(text(
            "SELECT SUM(CAST(per_ocu AS INT)) FROM seguridad.victimas_raw"
        )).scalar()
        stats["total_victimas_conflicto"] = int(vic) if vic else 0

        # Hechos victimizantes principales
        hechos = conn.execute(text("""
            SELECT hecho, SUM(CAST(per_ocu AS INT)) as total
            FROM seguridad.victimas_raw
            WHERE per_ocu IS NOT NULL
            GROUP BY hecho
            ORDER BY total DESC
            LIMIT 5
        """)).fetchall()
        stats["principales_hechos_victimizantes"] = [
            {"hecho": r[0], "personas": r[1]} for r in hechos
        ]

        # Servicios públicos
        stats["prestadores_servicios"] = conn.execute(text(
            "SELECT COUNT(*) FROM servicios.prestadores_raw"
        )).scalar()

    return stats


@router.get("/data-catalog")
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
