#!/usr/bin/env python3
"""
ETL Pipeline Sprint 1 - Observatorio de Ciudades Apartado
Carga los datasets nuevos descargados en Sprint 1 a PostgreSQL
y genera un reporte de completitud de datos.

Uso:
    python 04_load_sprint1.py
"""

import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

# ============================================================
# CONFIGURACION
# ============================================================
from config import MUNICIPIOS, URABA_DANE_CODES, DB_URL
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = BASE_DIR / "docs"

engine = create_engine(DB_URL)

# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def clean_columns(df):
    """Normaliza nombres de columnas: minusculas, sin espacios."""
    df.columns = [str(c) for c in df.columns]
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r'[^\w]+', '_', regex=True)
        .str.strip('_')
    )
    return df


def find_dane_col(df):
    """Intenta encontrar una columna con codigos DANE municipio."""
    candidates = ['municipio_id', 'cod_mpio', 'codigo_municipio', 'codigo_dane', 'cod_dane_municipio', 'municipio_codigo']
    for c in df.columns:
        if c in candidates: return c
    # Look for 05045 in values
    for c in df.columns:
        if df[c].astype(str).str.contains('05045').any(): return c
    return None


def load_dataset(rel_path, schema, table, expected):
    """Carga un dataset JSON a PostgreSQL. Retorna dict con resultado."""
    filepath = DATA_DIR / rel_path
    full_table = f"{schema}.{table}"

    if not filepath.exists():
        return {"table": full_table, "status": "skip", "rows": 0, "detail": "File not found"}

    try:
        df = load_json_to_df(filepath)
        df = clean_columns(df)

        # Detect DANE column and filter
        dane_col = find_dane_col(df)
        if dane_col:
            df = df[df[dane_col].astype(str).str.contains('|'.join(URABA_DANE_CODES))]
            df['dane_code'] = df[dane_col].astype(str).str.extract(f"({'|'.join(URABA_DANE_CODES)})")[0]
        else:
            # If no DANE col, assume it's Apartado for now or generic regional
            df['dane_code'] = '05045' # Default to Apartado if unknown

        # Ensure schema exists
        with engine.connect() as conn:
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
            conn.commit()

        # Handle columns with objects
        for col in df.columns:
            if any(isinstance(v, (dict, list)) for v in df[col].dropna().head(5)):
                df[col] = df[col].apply(lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, (dict, list)) else x)

        df.to_sql(table, engine, schema=schema, if_exists='append', index=False, method='multi', chunksize=1000)

        print(f"  [OK]   {full_table}: {len(df)} filas")
        return {"table": full_table, "status": "ok", "rows": len(df)}

    except Exception as e:
        print(f"  [FAIL] {full_table}: {e}")
        return {"table": full_table, "status": "error", "rows": 0, "detail": str(e)}

def truncate_tables():
    """Limpia las tablas antes de la carga regional."""
    with engine.connect() as conn:
        for _, schema, table, _ in DATASETS:
            conn.execute(text(f"DROP TABLE IF EXISTS {schema}.{table} CASCADE"))
        conn.commit()

def main():
    print("=" * 60)
    print("ETL Sprint 1 -- REGIONAL URABÁ")
    print("=" * 60)

    truncate_tables()
    
    results = []
    for rel_path, schema, table, expected in DATASETS:
        # Check if file exists as is, or if we should look for per-municipality files
        if "{name}" in rel_path:
             for dane_code, name, _ in MUNICIPIOS:
                 m_path = rel_path.replace("{name}", name.lower().replace(" ", "_"))
                 results.append(load_dataset(m_path, schema, table, expected))
        else:
             results.append(load_dataset(rel_path, schema, table, expected))

    generate_completeness_report()
    return 0

# ============================================================
# DATASETS A CARGAR
# ============================================================
DATASETS = [
    # SALUD
    ("salud/irca_calidad_agua.json",              "socioeconomico", "irca_raw",                    18),
    ("salud/sivigila_eventos.json",                "socioeconomico", "sivigila_raw",              2441),
    # ECONOMIA
    ("economia/secop_integrado.json",              "servicios",      "secop_raw",                25584),
    ("economia/eva_agricola.json",                 "socioeconomico", "eva_agricola_raw",            86),
    ("economia/eva_agricola_historico.json",        "socioeconomico", "eva_agricola_historico_raw", 162),
    # SEGURIDAD
    ("seguridad/lesiones_personales.json",         "seguridad",      "lesiones_personales_raw",   3653),
    ("seguridad/accidentes_transito_vehiculos.json","seguridad",     "accidentes_transito_raw",   1126),
    ("seguridad/minas_antipersonal_eventos.json",  "seguridad",      "minas_antipersonal_raw",     125),
    ("seguridad/minas_antipersonal_victimas.json", "seguridad",      "minas_victimas_raw",          45),
    ("seguridad/sievcac_masacres.json",            "seguridad",      "masacres_raw",                70),
    ("seguridad/sievcac_minas_victimas.json",      "seguridad",      "sievcac_minas_raw",           53),
    ("seguridad/siniestros_viales_criticos.json",  "seguridad",      "siniestros_viales_raw",        3),
    # INFRAESTRUCTURA
    ("infraestructura/internet_fijo.json",         "servicios",      "internet_fijo_raw",         9310),
    # GOBIERNO
    ("gobierno/familias_en_accion.json",           "socioeconomico", "familias_en_accion_raw",   18345),
    ("gobierno/icbf_prevencion.json",              "socioeconomico", "icbf_prevencion_raw",       2099),
    ("gobierno/icbf_primera_infancia.json",        "socioeconomico", "icbf_primera_infancia_raw",  801),
    ("gobierno/indice_gobierno_digital.json",      "socioeconomico", "gobierno_digital_raw",        84),
    ("gobierno/ungrd_emergencias.json",            "socioeconomico", "ungrd_emergencias_raw",       32),
    ("gobierno/puestos_votacion_2023.json",        "socioeconomico", "puestos_votacion_raw",        27),
    ("gobierno/colombia_mayor_directo.json",       "socioeconomico", "colombia_mayor_raw",           2),
    # EDUCACION
    ("educacion/sedes_educativas_geo.json",        "socioeconomico", "sedes_educativas_geo_raw",   75),
    # CULTURA
    ("cultura/rnt_turismo.json",                   "servicios",      "rnt_turismo_raw",            816),
    ("cultura/espacios_culturales.json",           "servicios",      "espacios_culturales_raw",     25),
]

# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def clean_columns(df):
    """Normaliza nombres de columnas: minusculas, sin espacios."""
    # Ensure all column names are strings first
    df.columns = [str(c) for c in df.columns]
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r'[^\w]+', '_', regex=True)
        .str.strip('_')
    )
    return df


def load_json_to_df(filepath):
    """Lee un archivo JSON y retorna un DataFrame."""
    with open(filepath, 'r', encoding='utf-8') as f:
        raw = json.load(f)

    if isinstance(raw, list):
        # If the list has mixed types (strings and dicts), filter to dicts only
        if raw and any(isinstance(x, dict) for x in raw) and any(isinstance(x, str) for x in raw):
            dict_items = [x for x in raw if isinstance(x, dict)]
            if dict_items:
                return pd.DataFrame(dict_items)
        return pd.DataFrame(raw)

    if isinstance(raw, dict):
        for key in ['data', 'results', 'records', 'features', 'items', 'rows', 'value']:
            if key in raw and isinstance(raw[key], list):
                return pd.DataFrame(raw[key])
        for key, val in raw.items():
            if isinstance(val, list) and len(val) > 0:
                return pd.DataFrame(val)
        return pd.DataFrame([raw])

    raise ValueError(f"Formato JSON no reconocido en {filepath}")


def load_dataset(rel_path, schema, table, expected):
    """Carga un dataset JSON a PostgreSQL. Retorna dict con resultado."""
    filepath = DATA_DIR / rel_path
    full_table = f"{schema}.{table}"

    if not filepath.exists():
        msg = f"Archivo no encontrado: {filepath}"
        print(f"  [FAIL] {full_table}: {msg}")
        return {"table": full_table, "status": "error", "rows": 0, "detail": msg}

    try:
        df = load_json_to_df(filepath)
        df = clean_columns(df)

        # Convertir columnas con listas/dicts anidados a string JSON
        for col in df.columns:
            sample = df[col].dropna().head(5)
            if any(isinstance(v, (dict, list)) for v in sample):
                df[col] = df[col].apply(
                    lambda x: json.dumps(x, ensure_ascii=False, default=str)
                    if isinstance(x, (dict, list)) else x
                )

        # Truncar strings muy largos
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].apply(
                lambda x: str(x)[:10000] if isinstance(x, str) and len(x) > 10000 else x
            )

        # Asegurar que el schema existe
        with engine.connect() as conn:
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
            conn.commit()

        df.to_sql(
            table,
            engine,
            schema=schema,
            if_exists='replace',
            index=False,
            method='multi',
            chunksize=1000,
        )

        loaded = len(df)
        detail = ""
        if loaded != expected:
            detail = f" (esperados: {expected})"

        print(f"  [OK]   {full_table}: {loaded} filas cargadas{detail}")
        return {"table": full_table, "status": "ok", "rows": loaded, "detail": detail.strip()}

    except Exception as e:
        msg = str(e)[:200]
        print(f"  [FAIL] {full_table}: {msg}")
        traceback.print_exc()
        return {"table": full_table, "status": "error", "rows": 0, "detail": msg}


# ============================================================
# DIMENSIONES DEL PLAN (11 dimensiones)
# ============================================================
DIMENSION_MAP = {
    "demografia": {
        "description": "Poblacion y proyecciones demograficas",
        "expected_tables": ["socioeconomico.terridata"],
        "missing_conceptual": ["proyecciones_dane", "censo_basico"]
    },
    "educacion": {
        "description": "Calidad educativa, cobertura, infraestructura",
        "expected_tables": [
            "socioeconomico.icfes_raw",
            "socioeconomico.establecimientos_educativos_raw",
            "socioeconomico.sedes_educativas_geo_raw",
        ],
        "missing_conceptual": ["matriculas_simat", "desercion_escolar"]
    },
    "salud": {
        "description": "Prestadores de salud, vigilancia epidemiologica, calidad del agua",
        "expected_tables": [
            "socioeconomico.ips_raw",
            "servicios.prestadores_raw",
            "socioeconomico.irca_raw",
            "socioeconomico.sivigila_raw",
        ],
        "missing_conceptual": ["mortalidad_infantil", "cobertura_vacunacion"]
    },
    "seguridad": {
        "description": "Delincuencia, conflicto armado, siniestralidad vial",
        "expected_tables": [
            "seguridad.homicidios_raw",
            "seguridad.hurtos_raw",
            "seguridad.delitos_sexuales_raw",
            "seguridad.violencia_intrafamiliar_raw",
            "seguridad.victimas_raw",
            "seguridad.lesiones_personales_raw",
            "seguridad.accidentes_transito_raw",
            "seguridad.minas_antipersonal_raw",
            "seguridad.minas_victimas_raw",
            "seguridad.masacres_raw",
            "seguridad.sievcac_minas_raw",
            "seguridad.siniestros_viales_raw",
        ],
        "missing_conceptual": ["extorsion", "secuestro"]
    },
    "economia": {
        "description": "Produccion agricola, contratacion publica, empleo",
        "expected_tables": [
            "socioeconomico.eva_agricola_raw",
            "socioeconomico.eva_agricola_historico_raw",
            "servicios.secop_raw",
        ],
        "missing_conceptual": ["empleo_dane", "pib_municipal", "catastro"]
    },
    "pobreza": {
        "description": "IPM, NBI, programas sociales",
        "expected_tables": [
            "socioeconomico.ipm_raw",
            "socioeconomico.nbi_raw",
            "socioeconomico.familias_en_accion_raw",
            "socioeconomico.colombia_mayor_raw",
        ],
        "missing_conceptual": ["gini_municipal"]
    },
    "infancia_y_familia": {
        "description": "Proteccion de primera infancia, prevencion",
        "expected_tables": [
            "socioeconomico.icbf_prevencion_raw",
            "socioeconomico.icbf_primera_infancia_raw",
        ],
        "missing_conceptual": ["adopciones", "trabajo_infantil"]
    },
    "infraestructura_y_servicios": {
        "description": "Conectividad, servicios publicos, vias",
        "expected_tables": [
            "servicios.internet_fijo_raw",
            "servicios.google_places",
            "cartografia.osm_vias",
            "cartografia.osm_edificaciones",
        ],
        "missing_conceptual": ["acueducto_cobertura", "alcantarillado_cobertura", "energia_cobertura"]
    },
    "gobierno_y_participacion": {
        "description": "Gobierno digital, emergencias, participacion ciudadana",
        "expected_tables": [
            "socioeconomico.gobierno_digital_raw",
            "socioeconomico.ungrd_emergencias_raw",
            "socioeconomico.puestos_votacion_raw",
        ],
        "missing_conceptual": ["presupuesto_municipal", "plan_desarrollo"]
    },
    "territorio_y_ambiente": {
        "description": "Uso del suelo, areas protegidas, cartografia base",
        "expected_tables": [
            "cartografia.limite_municipal",
            "cartografia.manzanas_censales",
            "cartografia.osm_uso_suelo",
            "cartografia.osm_amenidades",
            "cartografia.igac_municipios",
        ],
        "missing_conceptual": ["deforestacion", "coberturas_ideam", "riesgos_pot"]
    },
    "cultura_y_turismo": {
        "description": "Turismo, espacios culturales, patrimonio",
        "expected_tables": [
            "servicios.rnt_turismo_raw",
            "servicios.espacios_culturales_raw",
        ],
        "missing_conceptual": ["patrimonio_cultural", "bibliotecas"]
    },
}


def generate_completeness_report():
    """Genera el reporte de completitud consultando todas las tablas en la BD."""
    print("\n" + "=" * 60)
    print("GENERANDO REPORTE DE COMPLETITUD")
    print("=" * 60)

    table_counts = {}
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT schemaname, tablename 
            FROM pg_tables 
            WHERE schemaname IN ('cartografia', 'socioeconomico', 'seguridad', 'servicios')
            ORDER BY schemaname, tablename
        """)).fetchall()

        for schema, table in rows:
            full_name = f"{schema}.{table}"
            try:
                count_result = conn.execute(
                    text(f'SELECT COUNT(*) FROM "{schema}"."{table}"')
                ).scalar()
                table_counts[full_name] = count_result
            except Exception as e:
                print(f"  [WARN] No se pudo contar {full_name}: {e}")
                table_counts[full_name] = 0

    dimensions = {}
    for full_name, count in sorted(table_counts.items()):
        schema = full_name.split('.')[0]
        if schema not in dimensions:
            dimensions[schema] = {"tables": [], "total_records": 0}
        dimensions[schema]["tables"].append({"name": full_name, "records": count})
        dimensions[schema]["total_records"] += count

    total_tables = len(table_counts)
    total_records = sum(table_counts.values())

    data_dictionary_coverage = {}
    for dim_name, dim_info in DIMENSION_MAP.items():
        available = []
        missing = []
        for expected_table in dim_info["expected_tables"]:
            if expected_table in table_counts and table_counts[expected_table] > 0:
                available.append(expected_table)
            else:
                missing.append(expected_table)
        for m in dim_info.get("missing_conceptual", []):
            missing.append(f"(pendiente) {m}")

        data_dictionary_coverage[dim_name] = {
            "description": dim_info["description"],
            "available": available,
            "missing": missing,
            "coverage_pct": round(
                len(available) / max(len(dim_info["expected_tables"]), 1) * 100, 1
            )
        }

    report = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "municipality": "Apartado (05045)",
        "total_tables": total_tables,
        "total_records": total_records,
        "dimensions": dimensions,
        "data_dictionary_coverage": data_dictionary_coverage,
    }

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = DOCS_DIR / "data_completeness_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n  Reporte guardado en: {report_path}")
    return report


def print_summary(report):
    """Imprime un resumen legible del reporte."""
    print("\n" + "=" * 60)
    print("RESUMEN DE COMPLETITUD -- Observatorio Apartado (05045)")
    print("=" * 60)
    print(f"  Generado: {report['generated']}")
    print(f"  Total tablas: {report['total_tables']}")
    print(f"  Total registros: {report['total_records']:,}")
    
    print("\n--- Por esquema de BD ---")
    for schema, info in sorted(report['dimensions'].items()):
        print(f"\n  {schema.upper()} ({len(info['tables'])} tablas, {info['total_records']:,} registros)")
        for t in info['tables']:
            print(f"    - {t['name']}: {t['records']:,} registros")

    print("\n--- Cobertura por dimension del plan ---")
    for dim, info in report['data_dictionary_coverage'].items():
        miss_tables = [m for m in info['missing'] if not m.startswith('(pendiente)')]
        miss_concept = [m for m in info['missing'] if m.startswith('(pendiente)')]
        pct = info['coverage_pct']
        bar = "#" * int(pct / 5) + "." * (20 - int(pct / 5))
        print(f"\n  {dim} [{bar}] {pct}%")
        print(f"    {info['description']}")
        if info['available']:
            for a in info['available']:
                print(f"      [OK] {a}")
        if miss_tables:
            for m in miss_tables:
                print(f"      [--] {m} (tabla vacia o ausente)")
        if miss_concept:
            for m in miss_concept:
                print(f"      [  ] {m}")

    print("\n" + "=" * 60)
    print("ETL Sprint 1 completado.")
    print("=" * 60)


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 60)
    print("ETL Sprint 1 -- Observatorio de Ciudades Apartado")
    print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base de datos: {DB_URL}")
    print(f"Datasets a cargar: {len(DATASETS)}")
    print("=" * 60)

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("  Conexion a PostgreSQL: OK\n")
    except Exception as e:
        print(f"  [FAIL] No se pudo conectar a PostgreSQL: {e}")
        sys.exit(1)

    results = []
    ok_count = 0
    fail_count = 0
    total_rows = 0

    for rel_path, schema, table, expected in DATASETS:
        result = load_dataset(rel_path, schema, table, expected)
        results.append(result)
        if result["status"] == "ok":
            ok_count += 1
            total_rows += result["rows"]
        else:
            fail_count += 1

    print(f"\n--- Carga completada: {ok_count} OK, {fail_count} errores, {total_rows:,} filas totales ---")

    report = generate_completeness_report()
    print_summary(report)

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
