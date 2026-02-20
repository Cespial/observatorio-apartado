#!/usr/bin/env python3
"""
ETL 03 - Load TerriData Excel into PostgreSQL (Regional Urabá)
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
from sqlalchemy import create_engine, text
from config import MUNICIPIOS, DB_URL

# -- Configuration -----------------------------------------------------------
DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "terridata"
SHEET_NAME = "Datos"
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
    if pd.isna(val): return np.nan
    if isinstance(val, (int, float)): return float(val)
    s = str(val).strip().replace(".", "").replace(",", ".")
    try: return float(s)
    except ValueError: return np.nan


def load_file(engine, file_path, dane_code):
    print(f"Reading {file_path} for {dane_code}...")
    df = pd.read_excel(file_path, sheet_name=SHEET_NAME)
    
    # Clean
    df = df[df["Código Entidad"].notna()].reset_index(drop=True)
    df.rename(columns=COL_MAP, inplace=True)
    
    df["dato_numerico"] = df["dato_numerico"].apply(parse_spanish_number)
    df["dane_code"] = dane_code
    
    for col in ["codigo_departamento", "codigo_entidad", "anio", "mes"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    df.to_sql(
        TABLE, engine, schema=SCHEMA, if_exists="append", index=False,
        method="multi", chunksize=500
    )
    print(f"  Inserted {len(df)} rows.")


def main():
    engine = create_engine(DB_URL)
    
    # Create table with dane_code
    ddl = f"""
    DROP TABLE IF EXISTS {FULL_TABLE} CASCADE;
    CREATE TABLE {FULL_TABLE} (
        id                  SERIAL,
        dane_code           VARCHAR(5),
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
        unidad_de_medida    TEXT,
        PRIMARY KEY (id, dane_code)
    );
    CREATE INDEX idx_terridata_dane ON {FULL_TABLE} (dane_code);
    """
    with engine.begin() as conn:
        conn.execute(text(ddl))

    for dane_code, name, _ in MUNICIPIOS:
        # Search for file like TerriData05045f.xlsx
        files = list(DATA_DIR.glob(f"*{dane_code}*.xls*"))
        if not files:
            print(f"  [SKIP] No file found for {name} ({dane_code})")
            continue
            
        for f in files:
            try:
                load_file(engine, f, dane_code)
            except Exception as e:
                print(f"  [ERROR] Loading {f}: {e}")

    print("Done.")

if __name__ == "__main__":
    main()

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
