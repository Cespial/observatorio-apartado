#!/usr/bin/env python3
"""
ETL 09 - Load critical data files into PostgreSQL tables.
Loads: homicidios, hurtos, VIF, delitos_sexuales, victimas, ICFES,
       IPS, establecimientos_educativos from JSON files in data/.
"""
import json
import os
import pandas as pd
import numpy as np
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DANE_APARTADO = "05045"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def safe_insert(engine, df, table_name, schema):
    """Insert DataFrame into table, handling errors gracefully."""
    try:
        df.to_sql(
            table_name, engine, schema=schema,
            if_exists="append", index=False,
            method="multi", chunksize=200,
        )
        return len(df)
    except Exception as e:
        print(f"  ERROR inserting into {schema}.{table_name}: {e}")
        # Try row-by-row as fallback
        count = 0
        for i in range(0, len(df), 50):
            chunk = df.iloc[i:i+50]
            try:
                chunk.to_sql(
                    table_name, engine, schema=schema,
                    if_exists="append", index=False,
                    method="multi", chunksize=50,
                )
                count += len(chunk)
            except Exception:
                pass
        return count


def load_homicidios(engine):
    """Load homicidios: fecha_hecho→fecha, cod_muni→cod_municipio, sexo→genero."""
    print("\n[1/8] Loading homicidios...")
    path = DATA_DIR / "seguridad" / "homicidios_apartado.json"
    if not path.exists():
        print("  SKIP: file not found")
        return 0

    data = load_json(path)
    df = pd.DataFrame(data)

    out = pd.DataFrame()
    out["dane_code"] = DANE_APARTADO
    out["fecha"] = pd.to_datetime(df["fecha_hecho"], errors="coerce")
    out["municipio"] = df.get("municipio", "APARTADO")
    out["cod_municipio"] = df.get("cod_muni", DANE_APARTADO)
    out["departamento"] = df.get("departamento", "ANTIOQUIA")
    out["genero"] = df.get("sexo", "")
    out["grupo_etario"] = df.get("zona", "")  # best available
    out["arma_medio"] = ""
    out["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce").fillna(0).astype(int)

    n = safe_insert(engine, out, "homicidios", "seguridad")
    print(f"  seguridad.homicidios: Loaded {n}/{len(df)} rows")
    return n


def load_hurtos(engine):
    """Load hurtos: fecha_hecho→fecha, armas_medios→arma_medio."""
    print("\n[2/8] Loading hurtos...")
    path = DATA_DIR / "seguridad" / "hurtos_apartado.json"
    if not path.exists():
        print("  SKIP: file not found")
        return 0

    data = load_json(path)
    df = pd.DataFrame(data)

    out = pd.DataFrame()
    out["dane_code"] = DANE_APARTADO
    out["fecha"] = pd.to_datetime(df["fecha_hecho"], errors="coerce")
    out["municipio"] = df.get("municipio", "APARTADO")
    out["cod_municipio"] = df.get("codigo_dane", DANE_APARTADO)
    out["departamento"] = df.get("departamento", "ANTIOQUIA")
    out["tipo_hurto"] = df.get("tipo_de_hurto", "")
    out["genero"] = df.get("genero", "")
    out["grupo_etario"] = df.get("grupo_etario", "")
    out["arma_medio"] = df.get("armas_medios", "")
    out["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce").fillna(0).astype(int)

    n = safe_insert(engine, out, "hurtos", "seguridad")
    print(f"  seguridad.hurtos: Loaded {n}/{len(df)} rows")
    return n


def load_vif(engine):
    """Load violencia intrafamiliar."""
    print("\n[3/8] Loading violencia intrafamiliar...")
    path = DATA_DIR / "seguridad" / "violencia_intrafamiliar_apartado.json"
    if not path.exists():
        print("  SKIP: file not found")
        return 0

    data = load_json(path)
    df = pd.DataFrame(data)

    out = pd.DataFrame()
    out["dane_code"] = DANE_APARTADO
    out["fecha"] = pd.to_datetime(df["fecha_hecho"], errors="coerce")
    out["municipio"] = df.get("municipio", "APARTADO")
    out["cod_municipio"] = df.get("codigo_dane", DANE_APARTADO)
    out["departamento"] = df.get("departamento", "ANTIOQUIA")
    out["genero"] = df.get("genero", "")
    out["grupo_etario"] = df.get("grupo_etario", "")
    out["arma_medio"] = df.get("armas_medios", "")
    out["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce").fillna(0).astype(int)

    n = safe_insert(engine, out, "violencia_intrafamiliar", "seguridad")
    print(f"  seguridad.violencia_intrafamiliar: Loaded {n}/{len(df)} rows")
    return n


def load_delitos_sexuales(engine):
    """Load delitos sexuales."""
    print("\n[4/8] Loading delitos sexuales...")
    path = DATA_DIR / "seguridad" / "delitos_sexuales_apartado.json"
    if not path.exists():
        print("  SKIP: file not found")
        return 0

    data = load_json(path)
    df = pd.DataFrame(data)

    out = pd.DataFrame()
    out["dane_code"] = DANE_APARTADO
    out["fecha"] = pd.to_datetime(df["fecha_hecho"], errors="coerce")
    out["municipio"] = df.get("municipio", "APARTADO")
    out["cod_municipio"] = df.get("codigo_dane", DANE_APARTADO)
    out["departamento"] = df.get("departamento", "ANTIOQUIA")
    out["genero"] = df.get("genero", "")
    out["grupo_etario"] = df.get("grupo_etario", "")
    out["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce").fillna(0).astype(int)

    n = safe_insert(engine, out, "delitos_sexuales", "seguridad")
    print(f"  seguridad.delitos_sexuales: Loaded {n}/{len(df)} rows")
    return n


def load_victimas(engine):
    """Load víctimas del conflicto."""
    print("\n[5/8] Loading víctimas del conflicto...")
    path = DATA_DIR / "conflicto" / "victimas_apartado.json"
    if not path.exists():
        print("  SKIP: file not found")
        return 0

    data = load_json(path)
    df = pd.DataFrame(data)

    out = pd.DataFrame()
    out["dane_code"] = DANE_APARTADO
    out["cod_municipio"] = df.get("cod_ciudad_muni", "5045").astype(str)
    out["municipio"] = df.get("ciudad_municipio", "Apartado")
    out["departamento"] = df.get("estado_depto", "Antioquia")
    out["hecho"] = df.get("hecho", "")
    out["sexo"] = df.get("sexo", "")
    out["etnia"] = df.get("etnia", "")
    out["ciclo_vital"] = df.get("ciclo_vital", "")
    out["discapacidad"] = df.get("discapacidad", "")
    out["personas"] = pd.to_numeric(df.get("per_ocu", 0), errors="coerce").fillna(0).astype(int)
    out["eventos"] = pd.to_numeric(df.get("eventos", 0), errors="coerce").fillna(0).astype(int)
    out["fecha_corte"] = pd.to_datetime(df.get("fecha_corte", ""), errors="coerce")

    n = safe_insert(engine, out, "victimas_conflicto", "seguridad")
    print(f"  seguridad.victimas_conflicto: Loaded {n}/{len(df)} rows")
    return n


def load_icfes(engine):
    """Load ICFES Saber 11 results."""
    print("\n[6/8] Loading ICFES Saber 11...")
    path = DATA_DIR / "educacion" / "icfes_apartado.json"
    if not path.exists():
        print("  SKIP: file not found")
        return 0

    data = load_json(path)
    df = pd.DataFrame(data)

    out = pd.DataFrame()
    out["dane_code"] = DANE_APARTADO
    out["periodo"] = df.get("periodo", "").astype(str)
    out["cole_nombre"] = df.get("cole_nombre_establecimiento", "")
    out["cole_cod_dane"] = df.get("cole_cod_dane_establecimiento", "")
    out["cole_mcpio"] = df.get("cole_mcpio_ubicacion", "")
    out["estu_genero"] = df.get("estu_genero", "")

    # Score columns
    for col in ["punt_lectura_critica", "punt_matematicas", "punt_c_naturales", "punt_sociales", "punt_ingles"]:
        src = col
        if src in df.columns:
            out[col] = pd.to_numeric(df[src], errors="coerce")
        else:
            out[col] = np.nan

    # Map alternative column names
    if "punt_sociales_ciudadanas" in df.columns and "punt_sociales" not in df.columns:
        out["punt_sociales"] = pd.to_numeric(df["punt_sociales_ciudadanas"], errors="coerce")

    # Compute punt_global as average of available scores
    score_cols = ["punt_lectura_critica", "punt_matematicas", "punt_c_naturales", "punt_sociales", "punt_ingles"]
    available = [c for c in score_cols if c in out.columns and out[c].notna().any()]
    if available:
        out["punt_global"] = out[available].mean(axis=1).round(2)
    else:
        out["punt_global"] = out.get("punt_matematicas", np.nan)

    n = safe_insert(engine, out, "icfes", "socioeconomico")
    print(f"  socioeconomico.icfes: Loaded {n}/{len(df)} rows")
    return n


def load_ips(engine):
    """Load IPS salud (health providers)."""
    print("\n[7/8] Loading IPS salud...")
    path = DATA_DIR / "salud" / "ips_apartado.json"
    if not path.exists():
        print("  SKIP: file not found")
        return 0

    data = load_json(path)
    df = pd.DataFrame(data)

    out = pd.DataFrame()
    out["dane_code"] = DANE_APARTADO
    out["codigo_habilitacion"] = df.get("codigoprestador", "")
    out["nombre"] = df.get("nombreprestador", "")
    out["municipio"] = df.get("municipioprestadordesc", "APARTADÓ")
    out["cod_municipio"] = df.get("municipio_prestador", DANE_APARTADO)
    out["departamento"] = df.get("departamentoprestadordesc", "Antioquia")
    out["clase_persona"] = df.get("claseprestador", "")
    out["nivel_atencion"] = ""
    out["caracter"] = ""
    out["direccion"] = df.get("direcci_nsede", df.get("direccionprestador", ""))
    out["telefono"] = df.get("t_lefonosede", df.get("telefonoprestador", ""))

    n = safe_insert(engine, out, "ips_salud", "socioeconomico")
    print(f"  socioeconomico.ips_salud: Loaded {n}/{len(df)} rows")
    return n


def load_establecimientos(engine):
    """Load establecimientos educativos."""
    print("\n[8/8] Loading establecimientos educativos...")
    path = DATA_DIR / "educacion" / "establecimientos_apartado.json"
    if not path.exists():
        print("  SKIP: file not found")
        return 0

    data = load_json(path)
    df = pd.DataFrame(data)

    out = pd.DataFrame()
    out["dane_code"] = DANE_APARTADO
    out["codigo_dane"] = df.get("codigo_dane", "")
    out["nombre"] = df.get("nombre_establecimiento", "")
    out["municipio"] = df.get("municipio", "Apartadó")
    out["cod_municipio"] = df.get("cod_dane_municipio", "5045").astype(str)
    out["sector"] = df.get("sector", "")
    out["calendario"] = df.get("calendario", "")
    out["direccion"] = df.get("direccion", "")
    out["telefono"] = ""
    out["total_matricula"] = pd.to_numeric(df.get("total_matricula", 0), errors="coerce").fillna(0).astype(int)
    out["cantidad_sedes"] = pd.to_numeric(df.get("cantidad_sedes", 0), errors="coerce").fillna(0).astype(int)

    n = safe_insert(engine, out, "establecimientos_educativos", "socioeconomico")
    print(f"  socioeconomico.establecimientos_educativos: Loaded {n}/{len(df)} rows")
    return n


def main():
    if not DB_URL:
        print("ERROR: DATABASE_URL not set")
        return

    engine = create_engine(DB_URL)
    print("=" * 60)
    print("  Loading critical data into Supabase")
    print("=" * 60)

    total = 0
    total += load_homicidios(engine)
    total += load_hurtos(engine)
    total += load_vif(engine)
    total += load_delitos_sexuales(engine)
    total += load_victimas(engine)
    total += load_icfes(engine)
    total += load_ips(engine)
    total += load_establecimientos(engine)

    print("\n" + "=" * 60)
    print(f"  COMPLETE: {total} total rows loaded")
    print("=" * 60)

    # Verify counts
    with engine.connect() as conn:
        for tbl in [
            "seguridad.homicidios", "seguridad.hurtos",
            "seguridad.violencia_intrafamiliar", "seguridad.delitos_sexuales",
            "seguridad.victimas_conflicto", "socioeconomico.icfes",
            "socioeconomico.ips_salud", "socioeconomico.establecimientos_educativos",
        ]:
            cnt = conn.execute(text(f"SELECT COUNT(*) FROM {tbl}")).scalar()
            print(f"  {tbl}: {cnt} rows")


if __name__ == "__main__":
    main()
