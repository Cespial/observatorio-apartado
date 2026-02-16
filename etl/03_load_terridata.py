#!/usr/bin/env python3
"""
ETL 03 - Load TerriData Excel into PostgreSQL
Target: socioeconomico.terridata
Source: data/terridata/TerriData05045f.xlsx  (sheet 'Datos')
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text

# -- Configuration -----------------------------------------------------------
EXCEL_PATH = "/Users/cristianespinal/observatorio-apartado/data/terridata/TerriData05045f.xlsx"
SHEET_NAME = "Datos"
DB_URL = "postgresql://cristianespinal@localhost:5433/observatorio_apartado"
SCHEMA = "socioeconomico"
TABLE = "terridata"
FULL_TABLE = SCHEMA + "." + TABLE

# -- Column mapping: original Spanish -> snake_case --------------------------
COL_MAP = {
    "Código Departamento": "codigo_departamento",
    "Departamento": "departamento",
    "Código Entidad": "codigo_entidad",
    "Entidad": "entidad",
    "Dimensión": "dimension",
    "Subcategoría": "subcategoria",
    "Indicador": "indicador",
    "Dato Numérico": "dato_numerico",
    "Dato Cualitativo": "dato_cualitativo",
    "Año": "anio",
    "Mes": "mes",
    "Fuente": "fuente",
    "Unidad de Medida": "unidad_de_medida",
}


def parse_spanish_number(val):
    """Convert Spanish-formatted number string (dots=thousands, comma=decimal)
    to float.  e.g. '58.868.473.856,00' -> 58868473856.0"""
    if pd.isna(val):
        return np.nan
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    if s == "":
        return np.nan
    # Remove thousands separator (dots), then replace comma with period
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return np.nan


def main():
    # -- 1. Read Excel -------------------------------------------------------
    print("Reading " + EXCEL_PATH + " sheet='" + SHEET_NAME + "' ...")
    df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME)
    print("  Raw rows read: " + str(len(df)))

    # -- 2. Drop junk first row (all 'a' chars, Codigo Entidad is NaN) ------
    junk_mask = df["Código Entidad"].isna() & df["Código Departamento"].isna()
    n_junk = junk_mask.sum()
    df = df[~junk_mask].reset_index(drop=True)
    print("  Junk rows removed: " + str(n_junk))
    print("  Clean rows: " + str(len(df)))

    # -- 3. Rename columns to snake_case -------------------------------------
    df.rename(columns=COL_MAP, inplace=True)

    # -- 4. Fix dato_numerico: Spanish number format -> float ----------------
    print("\nConverting dato_numerico from Spanish number format ...")
    sample_before = df["dato_numerico"].dropna().head(5).tolist()
    print("  Sample before: " + str(sample_before))

    df["dato_numerico"] = df["dato_numerico"].apply(parse_spanish_number)

    sample_after = df["dato_numerico"].dropna().head(5).tolist()
    print("  Sample after:  " + str(sample_after))
    print("  Non-null count: " + str(df["dato_numerico"].notna().sum()))

    # -- 5. Cast integer-like columns ----------------------------------------
    for col in ["codigo_departamento", "codigo_entidad", "anio", "mes"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].astype("Int64")

    print("\nColumn dtypes after cleaning:")
    for c in df.columns:
        print("  %-25s  %s" % (c, df[c].dtype))

    # -- 6. Connect to PostgreSQL and create table ---------------------------
    engine = create_engine(DB_URL)

    ddl = """
    DROP TABLE IF EXISTS """ + FULL_TABLE + """ CASCADE;
    CREATE TABLE """ + FULL_TABLE + """ (
        id                  SERIAL PRIMARY KEY,
        codigo_departamento INTEGER,
        departamento        TEXT,
        codigo_entidad      INTEGER,
        entidad             TEXT,
        dimension           TEXT,
        subcategoria        TEXT,
        indicador           TEXT,
        dato_numerico       DOUBLE PRECISION,
        dato_cualitativo    TEXT,
        anio                INTEGER,
        mes                 INTEGER,
        fuente              TEXT,
        unidad_de_medida    TEXT
    );
    """

    with engine.begin() as conn:
        conn.execute(text(ddl))
    print("\nTable " + FULL_TABLE + " created.")

    # -- 7. Load data via to_sql (append into the table we just created) -----
    df.to_sql(
        TABLE,
        engine,
        schema=SCHEMA,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=500,
    )
    print("Inserted " + str(len(df)) + " rows into " + FULL_TABLE + ".")

    # -- 8. Create indexes ---------------------------------------------------
    idx_stmts = [
        "CREATE INDEX idx_terridata_dimension  ON " + FULL_TABLE + " (dimension);",
        "CREATE INDEX idx_terridata_indicador  ON " + FULL_TABLE + " (indicador);",
        "CREATE INDEX idx_terridata_anio       ON " + FULL_TABLE + " (anio);",
    ]
    with engine.begin() as conn:
        for stmt in idx_stmts:
            conn.execute(text(stmt))
    print("Indexes created on: dimension, indicador, anio.")

    # -- 9. Summary stats ----------------------------------------------------
    with engine.connect() as conn:
        row_count = conn.execute(
            text("SELECT count(*) FROM " + FULL_TABLE)
        ).scalar()
        dims = conn.execute(
            text("SELECT DISTINCT dimension FROM " + FULL_TABLE + " ORDER BY 1")
        ).fetchall()
        year_range = conn.execute(
            text("SELECT min(anio), max(anio) FROM " + FULL_TABLE)
        ).fetchone()
        top_indicators = conn.execute(
            text(
                "SELECT indicador, count(*) AS n FROM " + FULL_TABLE
                + " GROUP BY indicador ORDER BY n DESC LIMIT 10"
            )
        ).fetchall()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("Total rows loaded:  " + str(row_count))
    print("Year range:         " + str(year_range[0]) + " - " + str(year_range[1]))
    print("Distinct dimensions (" + str(len(dims)) + "):")
    for d in dims:
        print("  - " + str(d[0]))
    print("\nTop 10 indicators by row count:")
    for ind, n in top_indicators:
        print("  %5d  %s" % (n, ind))
    print("=" * 70)
    print("Done.")


if __name__ == "__main__":
    main()
