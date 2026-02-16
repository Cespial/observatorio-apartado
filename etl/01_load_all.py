#!/usr/bin/env python3
"""
ETL Pipeline — Observatorio de Ciudades Apartadó
Carga todos los datasets a PostgreSQL/PostGIS
"""
import json
import os
import sys
import traceback
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text

# ============================================================
# CONFIGURACIÓN
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

from dotenv import load_dotenv
load_dotenv(BASE_DIR / ".env")

DB_URL = os.getenv("DATABASE_URL")
DANE_CODE = os.getenv("DANE_CODE", "05045")

engine = create_engine(DB_URL)

results = []

def log(msg):
    print(f"  {msg}")

def report(name, status, count=0, detail=""):
    results.append({"dataset": name, "status": status, "registros": count, "detalle": detail})
    emoji = "OK" if status == "ok" else "FAIL" if status == "error" else "SKIP"
    print(f"  [{emoji}] {name}: {count} registros {detail}")


# ============================================================
# 1. CARTOGRAFÍA — Límite municipal
# ============================================================
def load_limite_municipal():
    log("Cargando límite municipal de Apartadó...")
    path = DATA_DIR / "cartografia" / "geojson" / "apartado.geojson"
    if not path.exists():
        report("limite_municipal", "error", detail="Archivo no encontrado")
        return
    gdf = gpd.read_file(path)
    gdf = gdf.to_crs(epsg=4326)
    gdf_out = gpd.GeoDataFrame({
        "nombre": [gdf.iloc[0].get("name", "Apartadó")],
        "divipola": [gdf.iloc[0].get("divipola", DANE_CODE)],
        "departamento": [gdf.iloc[0].get("is_in:state", "Antioquia")],
        "area_km2": [gdf.iloc[0].get("DANE:area", None)],
        "geom": [gdf.iloc[0].geometry]
    }, geometry="geom", crs="EPSG:4326")
    gdf_out.to_postgis("limite_municipal", engine, schema="cartografia", if_exists="replace", index=False)
    report("limite_municipal", "ok", len(gdf_out))


# ============================================================
# 2. OSM — Edificaciones, Vías, Uso suelo, Amenidades
# ============================================================
def load_osm_buildings():
    log("Cargando edificaciones OSM...")
    path = DATA_DIR / "cartografia" / "osm" / "apartado_buildings.json"
    if not path.exists():
        report("osm_edificaciones", "error", detail="Archivo no encontrado")
        return
    with open(path) as f:
        data = json.load(f)

    rows = []
    for el in data.get("elements", []):
        if el.get("type") != "way" or "geometry" not in el:
            continue
        coords = [(p["lon"], p["lat"]) for p in el["geometry"]]
        if len(coords) < 4:
            continue
        if coords[0] != coords[-1]:
            coords.append(coords[0])
        from shapely.geometry import Polygon
        try:
            poly = Polygon(coords)
            if not poly.is_valid:
                poly = poly.buffer(0)
            tags = el.get("tags", {})
            rows.append({
                "id": el["id"],
                "osm_type": "way",
                "building": tags.get("building", "yes"),
                "name": tags.get("name"),
                "amenity": tags.get("amenity"),
                "addr_street": tags.get("addr:street"),
                "geom": poly
            })
        except Exception:
            continue

    if rows:
        gdf = gpd.GeoDataFrame(rows, geometry="geom", crs="EPSG:4326")
        gdf.to_postgis("osm_edificaciones", engine, schema="cartografia", if_exists="replace", index=False)
        report("osm_edificaciones", "ok", len(gdf))
    else:
        report("osm_edificaciones", "error", detail="Sin datos")


def load_osm_roads():
    log("Cargando vías OSM...")
    path = DATA_DIR / "cartografia" / "osm" / "apartado_roads.json"
    if not path.exists():
        report("osm_vias", "error", detail="Archivo no encontrado")
        return
    with open(path) as f:
        data = json.load(f)

    rows = []
    for el in data.get("elements", []):
        if el.get("type") != "way" or "geometry" not in el:
            continue
        coords = [(p["lon"], p["lat"]) for p in el["geometry"]]
        if len(coords) < 2:
            continue
        from shapely.geometry import LineString
        try:
            line = LineString(coords)
            tags = el.get("tags", {})
            rows.append({
                "id": el["id"],
                "osm_type": "way",
                "highway": tags.get("highway"),
                "name": tags.get("name"),
                "surface": tags.get("surface"),
                "lanes": int(tags["lanes"]) if "lanes" in tags else None,
                "geom": line
            })
        except Exception:
            continue

    if rows:
        gdf = gpd.GeoDataFrame(rows, geometry="geom", crs="EPSG:4326")
        gdf.to_postgis("osm_vias", engine, schema="cartografia", if_exists="replace", index=False)
        report("osm_vias", "ok", len(gdf))
    else:
        report("osm_vias", "error", detail="Sin datos")


def load_osm_landuse():
    log("Cargando uso del suelo OSM...")
    path = DATA_DIR / "cartografia" / "osm" / "apartado_landuse.json"
    if not path.exists():
        report("osm_uso_suelo", "error", detail="Archivo no encontrado")
        return
    with open(path) as f:
        data = json.load(f)

    rows = []
    for el in data.get("elements", []):
        if el.get("type") != "way" or "geometry" not in el:
            continue
        coords = [(p["lon"], p["lat"]) for p in el["geometry"]]
        if len(coords) < 4:
            continue
        if coords[0] != coords[-1]:
            coords.append(coords[0])
        from shapely.geometry import Polygon
        try:
            poly = Polygon(coords)
            if not poly.is_valid:
                poly = poly.buffer(0)
            tags = el.get("tags", {})
            rows.append({
                "id": el["id"],
                "landuse": tags.get("landuse"),
                "name": tags.get("name"),
                "geom": poly
            })
        except Exception:
            continue

    if rows:
        gdf = gpd.GeoDataFrame(rows, geometry="geom", crs="EPSG:4326")
        gdf.to_postgis("osm_uso_suelo", engine, schema="cartografia", if_exists="replace", index=False)
        report("osm_uso_suelo", "ok", len(gdf))
    else:
        report("osm_uso_suelo", "error", detail="Sin datos")


def load_osm_amenities():
    log("Cargando amenidades OSM...")
    path = DATA_DIR / "cartografia" / "osm" / "apartado_amenities.json"
    if not path.exists():
        report("osm_amenidades", "error", detail="Archivo no encontrado")
        return
    with open(path) as f:
        data = json.load(f)

    rows = []
    for el in data.get("elements", []):
        if "lat" not in el or "lon" not in el:
            continue
        from shapely.geometry import Point
        tags = el.get("tags", {})
        rows.append({
            "id": el["id"],
            "amenity": tags.get("amenity"),
            "name": tags.get("name"),
            "phone": tags.get("phone"),
            "website": tags.get("website"),
            "opening_hours": tags.get("opening_hours"),
            "lat": el["lat"],
            "lon": el["lon"],
            "geom": Point(el["lon"], el["lat"])
        })

    if rows:
        gdf = gpd.GeoDataFrame(rows, geometry="geom", crs="EPSG:4326")
        gdf.to_postgis("osm_amenidades", engine, schema="cartografia", if_exists="replace", index=False)
        report("osm_amenidades", "ok", len(gdf))
    else:
        report("osm_amenidades", "error", detail="Sin datos")


# ============================================================
# 3. MGN — Manzanas Censales (filtrar Apartadó)
# ============================================================
def load_mgn_manzanas():
    log("Cargando MGN manzanas censales (filtrando Apartadó)...")
    shp_path = DATA_DIR / "cartografia" / "mgn" / "raw" / "MGN_ANM_MANZANA.shp"
    if not shp_path.exists():
        report("manzanas_censales", "error", detail="Shapefile no encontrado")
        return

    # Read only Apartadó using a bounding box filter first, then DANE code
    log("  Leyendo shapefile nacional (puede tardar)...")
    # Read the DBF to find column names first
    sample = gpd.read_file(shp_path, rows=5)
    log(f"  Columnas: {list(sample.columns)}")

    # Find the municipality code column
    mpio_col = None
    for col in sample.columns:
        if "mpio" in col.lower() or "municipio" in col.lower() or "cod_mun" in col.lower():
            log(f"  Columna municipio candidata: {col} = {sample[col].iloc[0]}")
            mpio_col = col

    # Use bbox to pre-filter (Apartadó: approx 7.77, -76.75, 8.07, -76.41)
    log("  Filtrando por bounding box de Apartadó...")
    gdf = gpd.read_file(shp_path, bbox=(-76.80, 7.70, -76.35, 8.10))
    log(f"  Registros en bbox: {len(gdf)}")

    if len(gdf) == 0:
        report("manzanas_censales", "error", detail="Sin manzanas en bbox")
        return

    # Additional filter by DANE code if column found
    log(f"  Columnas disponibles: {list(gdf.columns)}")
    code_cols = [c for c in gdf.columns if 'mpio' in c.lower() or 'municipio' in c.lower() or '05045' in str(gdf[c].unique()[:5])]
    if code_cols:
        log(f"  Filtrando por columnas: {code_cols}")

    gdf = gdf.to_crs(epsg=4326)

    # Map columns dynamically
    col_map = {}
    for c in gdf.columns:
        cl = c.lower()
        if 'manz' in cl and ('cod' in cl or 'cdgo' in cl):
            col_map['cod_dane_manzana'] = c
        elif 'secc' in cl and ('cod' in cl or 'cdgo' in cl):
            col_map['cod_dane_seccion'] = c
        elif 'sect' in cl and ('cod' in cl or 'cdgo' in cl):
            col_map['cod_dane_sector'] = c
        elif cl in ('mpio_cdpmp', 'cod_mpio', 'mpio_ccdgo'):
            col_map['cod_dane_municipio'] = c
        elif 'tp_' in cl or 'total_per' in cl:
            col_map['total_personas'] = c
        elif 'th_' in cl or 'total_hog' in cl:
            col_map['total_hogares'] = c
        elif 'tv_' in cl or 'total_viv' in cl:
            col_map['total_viviendas'] = c

    log(f"  Mapeo de columnas: {col_map}")

    out_cols = {"geom": gdf.geometry}
    for target, source in col_map.items():
        out_cols[target] = gdf[source]

    gdf_out = gpd.GeoDataFrame(out_cols, geometry="geom", crs="EPSG:4326")
    gdf_out.to_postgis("manzanas_censales", engine, schema="cartografia", if_exists="replace", index=False)
    report("manzanas_censales", "ok", len(gdf_out))


# ============================================================
# 4. CATASTRO — Terrenos (filtrar Apartadó)
# ============================================================
def load_catastro_terrenos():
    log("Cargando catastro terrenos (filtrando Apartadó)...")
    shp_path = DATA_DIR / "catastro" / "raw" / "CatastroPubliconNoviembre2025" / "R_TERRENO.shp"
    if not shp_path.exists():
        report("catastro_terrenos", "error", detail="Shapefile no encontrado")
        return

    sample = gpd.read_file(shp_path, rows=3)
    log(f"  Columnas terreno: {list(sample.columns)}")

    # Filter by bbox
    log("  Filtrando por bbox...")
    gdf = gpd.read_file(shp_path, bbox=(-76.80, 7.70, -76.35, 8.10))
    log(f"  Terrenos en bbox: {len(gdf)}")

    if len(gdf) == 0:
        report("catastro_terrenos", "error", detail="Sin terrenos en bbox")
        return

    gdf = gdf.to_crs(epsg=4326)
    gdf.to_postgis("terrenos", engine, schema="catastro", if_exists="replace", index=False)
    report("catastro_terrenos", "ok", len(gdf))


def load_catastro_construcciones():
    log("Cargando catastro construcciones (filtrando Apartadó)...")
    shp_path = DATA_DIR / "catastro" / "raw" / "CatastroPubliconNoviembre2025" / "R_CONSTRUCCION.shp"
    if not shp_path.exists():
        report("catastro_construcciones", "error", detail="Shapefile no encontrado")
        return

    sample = gpd.read_file(shp_path, rows=3)
    log(f"  Columnas construcción: {list(sample.columns)}")

    gdf = gpd.read_file(shp_path, bbox=(-76.80, 7.70, -76.35, 8.10))
    log(f"  Construcciones en bbox: {len(gdf)}")

    if len(gdf) == 0:
        report("catastro_construcciones", "error", detail="Sin construcciones en bbox")
        return

    gdf = gdf.to_crs(epsg=4326)
    gdf.to_postgis("construcciones", engine, schema="catastro", if_exists="replace", index=False)
    report("catastro_construcciones", "ok", len(gdf))


def load_catastro_sectores():
    log("Cargando catastro sectores...")
    shp_path = DATA_DIR / "catastro" / "raw" / "CatastroPubliconNoviembre2025" / "R_SECTOR.shp"
    if not shp_path.exists():
        report("catastro_sectores", "error", detail="Shapefile no encontrado")
        return

    sample = gpd.read_file(shp_path, rows=3)
    log(f"  Columnas sector: {list(sample.columns)}")

    gdf = gpd.read_file(shp_path, bbox=(-76.80, 7.70, -76.35, 8.10))
    log(f"  Sectores en bbox: {len(gdf)}")

    if len(gdf) == 0:
        report("catastro_sectores", "error", detail="Sin sectores en bbox")
        return

    gdf = gdf.to_crs(epsg=4326)
    gdf.to_postgis("sectores", engine, schema="catastro", if_exists="replace", index=False)
    report("catastro_sectores", "ok", len(gdf))


def load_catastro_veredas():
    log("Cargando catastro veredas...")
    shp_path = DATA_DIR / "catastro" / "raw" / "CatastroPubliconNoviembre2025" / "R_VEREDA.shp"
    if not shp_path.exists():
        report("catastro_veredas", "error", detail="Shapefile no encontrado")
        return

    sample = gpd.read_file(shp_path, rows=3)
    log(f"  Columnas vereda: {list(sample.columns)}")

    gdf = gpd.read_file(shp_path, bbox=(-76.80, 7.70, -76.35, 8.10))
    log(f"  Veredas en bbox: {len(gdf)}")

    if len(gdf) == 0:
        report("catastro_veredas", "error", detail="Sin veredas en bbox")
        return

    gdf = gdf.to_crs(epsg=4326)
    gdf.to_postgis("veredas", engine, schema="catastro", if_exists="replace", index=False)
    report("catastro_veredas", "ok", len(gdf))


# ============================================================
# 5. IGAC — Municipios shapefile
# ============================================================
def load_igac_municipios():
    log("Cargando IGAC municipios...")
    shp_path = DATA_DIR / "cartografia" / "igac" / "raw" / "DireccionesTerritoriales_shp" / "DTerritorialesMunpio.shp"
    if not shp_path.exists():
        report("igac_municipios", "error", detail="Shapefile no encontrado")
        return

    gdf = gpd.read_file(shp_path, bbox=(-76.80, 7.70, -76.35, 8.10))
    log(f"  Municipios IGAC en bbox: {len(gdf)}")
    log(f"  Columnas: {list(gdf.columns)}")

    if len(gdf) > 0:
        gdf = gdf.to_crs(epsg=4326)
        gdf.to_postgis("igac_municipios", engine, schema="cartografia", if_exists="replace", index=False)
        report("igac_municipios", "ok", len(gdf))
    else:
        report("igac_municipios", "error", detail="Sin datos en bbox")


# ============================================================
# 6. SOCIOECONÓMICO — IPM
# ============================================================
def load_ipm():
    log("Cargando IPM municipal...")
    path = DATA_DIR / "socioeconomico" / "ipm" / "ipm_municipal.xls"
    if not path.exists():
        report("ipm", "error", detail="Archivo no encontrado")
        return

    try:
        df = pd.read_excel(path, engine="xlrd")
        log(f"  Columnas IPM: {list(df.columns)[:10]}...")
        log(f"  Shape: {df.shape}")
        log(f"  Primeras filas:\n{df.head(3).to_string()}")

        # Find code column with 05045
        for col in df.columns:
            if df[col].astype(str).str.contains("05045|5045").any():
                log(f"  Columna con código Apartadó: {col}")
                df_apt = df[df[col].astype(str).str.contains("05045|5045")]
                log(f"  Filas Apartadó: {len(df_apt)}")
                df_apt.to_sql("ipm_raw", engine, schema="socioeconomico", if_exists="replace", index=False)
                report("ipm", "ok", len(df_apt))
                return

        # If no specific filter found, load all
        df.to_sql("ipm_raw", engine, schema="socioeconomico", if_exists="replace", index=False)
        report("ipm", "ok", len(df), detail="(tabla completa)")
    except Exception as e:
        report("ipm", "error", detail=str(e)[:100])


# ============================================================
# 7. SOCIOECONÓMICO — NBI
# ============================================================
def load_nbi():
    log("Cargando NBI municipal...")
    path = DATA_DIR / "socioeconomico" / "nbi" / "nbi_municipios.xls"
    if not path.exists():
        report("nbi", "error", detail="Archivo no encontrado")
        return

    try:
        df = pd.read_excel(path, engine="xlrd")
        log(f"  Columnas NBI: {list(df.columns)[:10]}...")
        log(f"  Shape: {df.shape}")

        for col in df.columns:
            if df[col].astype(str).str.contains("05045|5045").any():
                df_apt = df[df[col].astype(str).str.contains("05045|5045")]
                log(f"  Filas Apartadó (col {col}): {len(df_apt)}")
                df_apt.to_sql("nbi_raw", engine, schema="socioeconomico", if_exists="replace", index=False)
                report("nbi", "ok", len(df_apt))
                return

        df.to_sql("nbi_raw", engine, schema="socioeconomico", if_exists="replace", index=False)
        report("nbi", "ok", len(df), detail="(tabla completa)")
    except Exception as e:
        report("nbi", "error", detail=str(e)[:100])


# ============================================================
# 8. EDUCACIÓN — Establecimientos
# ============================================================
def load_educacion():
    log("Cargando establecimientos educativos...")
    path = DATA_DIR / "educacion" / "establecimientos_apartado.json"
    if not path.exists():
        report("establecimientos_educativos", "error", detail="Archivo no encontrado")
        return

    with open(path) as f:
        data = json.load(f)

    if not data:
        report("establecimientos_educativos", "error", detail="Vacío")
        return

    df = pd.DataFrame(data)
    log(f"  Columnas: {list(df.columns)[:10]}")

    col_map = {}
    for c in df.columns:
        cl = c.lower()
        if 'codigo_dane' in cl and 'mun' not in cl:
            col_map['codigo_dane'] = c
        elif 'nombre' in cl and 'establecimiento' in cl:
            col_map['nombre'] = c
        elif 'municipio' == cl:
            col_map['municipio'] = c
        elif 'sector' == cl or 'cod_sector' == cl:
            col_map['sector'] = c
        elif 'total_matricula' in cl:
            col_map['total_matricula'] = c

    df.to_sql("establecimientos_educativos_raw", engine, schema="socioeconomico", if_exists="replace", index=False)
    report("establecimientos_educativos", "ok", len(df))


# ============================================================
# 9. EDUCACIÓN — ICFES
# ============================================================
def load_icfes():
    log("Cargando resultados ICFES...")
    path = DATA_DIR / "educacion" / "icfes_apartado.json"
    if not path.exists():
        report("icfes", "error", detail="Archivo no encontrado")
        return

    with open(path) as f:
        data = json.load(f)

    if not data:
        report("icfes", "error", detail="Vacío")
        return

    df = pd.DataFrame(data)
    log(f"  Columnas ICFES: {list(df.columns)[:15]}")
    log(f"  Registros: {len(df)}")

    # Convert numeric columns
    num_cols = [c for c in df.columns if 'punt_' in c.lower() or 'puntaje' in c.lower()]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')

    df.to_sql("icfes_raw", engine, schema="socioeconomico", if_exists="replace", index=False)
    report("icfes", "ok", len(df))


# ============================================================
# 10. SALUD — IPS
# ============================================================
def load_ips():
    log("Cargando IPS/Salud...")
    path = DATA_DIR / "salud" / "ips_apartado.json"
    if not path.exists():
        report("ips_salud", "error", detail="Archivo no encontrado")
        return

    with open(path) as f:
        data = json.load(f)

    if not data:
        report("ips_salud", "error", detail="Vacío")
        return

    df = pd.DataFrame(data)
    log(f"  Columnas IPS: {list(df.columns)[:10]}")
    df.to_sql("ips_raw", engine, schema="socioeconomico", if_exists="replace", index=False)
    report("ips_salud", "ok", len(df))


# ============================================================
# 11. SERVICIOS PÚBLICOS
# ============================================================
def load_servicios_publicos():
    log("Cargando prestadores de servicios públicos...")
    path = DATA_DIR / "servicios_publicos" / "prestadores_apartado.json"
    if not path.exists():
        report("servicios_publicos", "error", detail="Archivo no encontrado")
        return

    with open(path) as f:
        data = json.load(f)

    if not data:
        report("servicios_publicos", "error", detail="Vacío")
        return

    df = pd.DataFrame(data)
    log(f"  Columnas Servicios: {list(df.columns)[:10]}")
    df.to_sql("prestadores_raw", engine, schema="servicios", if_exists="replace", index=False)
    report("servicios_publicos", "ok", len(df))


# ============================================================
# 12-15. SEGURIDAD
# ============================================================
def load_security_dataset(name, filename, table_name):
    log(f"Cargando {name}...")
    path = DATA_DIR / "seguridad" / filename
    if not path.exists():
        report(name, "error", detail="Archivo no encontrado")
        return

    with open(path) as f:
        data = json.load(f)

    if not data or (isinstance(data, dict) and data.get("error")):
        report(name, "error", detail="Vacío o error API")
        return

    df = pd.DataFrame(data)

    # Convert fecha_hecho to date
    date_cols = [c for c in df.columns if 'fecha' in c.lower()]
    for c in date_cols:
        df[c] = pd.to_datetime(df[c], errors='coerce')

    # Convert cantidad to numeric
    if 'cantidad' in df.columns:
        df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce')

    df.to_sql(table_name, engine, schema="seguridad", if_exists="replace", index=False)
    report(name, "ok", len(df))


# ============================================================
# 16. CONFLICTO — Víctimas
# ============================================================
def load_victimas():
    log("Cargando víctimas del conflicto...")
    path = DATA_DIR / "conflicto" / "victimas_apartado.json"
    if not path.exists():
        report("victimas_conflicto", "error", detail="Archivo no encontrado")
        return

    with open(path) as f:
        data = json.load(f)

    if not data or (isinstance(data, dict) and data.get("error")):
        report("victimas_conflicto", "error", detail="Vacío o error API")
        return

    df = pd.DataFrame(data)
    log(f"  Columnas víctimas: {list(df.columns)[:10]}")

    num_cols = ['per_ocu', 'eventos', 'personas']
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')

    df.to_sql("victimas_raw", engine, schema="seguridad", if_exists="replace", index=False)
    report("victimas_conflicto", "ok", len(df))


# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================
def main():
    print("=" * 70)
    print("  ETL PIPELINE — OBSERVATORIO DE CIUDADES APARTADÓ")
    print("=" * 70)

    # Cartografía
    try: load_limite_municipal()
    except Exception as e: report("limite_municipal", "error", detail=str(e)[:100])

    try: load_osm_buildings()
    except Exception as e: report("osm_edificaciones", "error", detail=str(e)[:100])

    try: load_osm_roads()
    except Exception as e: report("osm_vias", "error", detail=str(e)[:100])

    try: load_osm_landuse()
    except Exception as e: report("osm_uso_suelo", "error", detail=str(e)[:100])

    try: load_osm_amenities()
    except Exception as e: report("osm_amenidades", "error", detail=str(e)[:100])

    try: load_igac_municipios()
    except Exception as e: report("igac_municipios", "error", detail=str(e)[:100])

    # MGN y Catastro (pesados)
    try: load_mgn_manzanas()
    except Exception as e:
        traceback.print_exc()
        report("manzanas_censales", "error", detail=str(e)[:100])

    try: load_catastro_terrenos()
    except Exception as e:
        traceback.print_exc()
        report("catastro_terrenos", "error", detail=str(e)[:100])

    try: load_catastro_construcciones()
    except Exception as e:
        traceback.print_exc()
        report("catastro_construcciones", "error", detail=str(e)[:100])

    try: load_catastro_sectores()
    except Exception as e:
        traceback.print_exc()
        report("catastro_sectores", "error", detail=str(e)[:100])

    try: load_catastro_veredas()
    except Exception as e:
        traceback.print_exc()
        report("catastro_veredas", "error", detail=str(e)[:100])

    # Socioeconómico
    try: load_ipm()
    except Exception as e: report("ipm", "error", detail=str(e)[:100])

    try: load_nbi()
    except Exception as e: report("nbi", "error", detail=str(e)[:100])

    try: load_educacion()
    except Exception as e: report("establecimientos_educativos", "error", detail=str(e)[:100])

    try: load_icfes()
    except Exception as e: report("icfes", "error", detail=str(e)[:100])

    try: load_ips()
    except Exception as e: report("ips_salud", "error", detail=str(e)[:100])

    try: load_servicios_publicos()
    except Exception as e: report("servicios_publicos", "error", detail=str(e)[:100])

    # Seguridad
    try: load_security_dataset("homicidios", "homicidios_apartado.json", "homicidios_raw")
    except Exception as e: report("homicidios", "error", detail=str(e)[:100])

    try: load_security_dataset("hurtos", "hurtos_apartado.json", "hurtos_raw")
    except Exception as e: report("hurtos", "error", detail=str(e)[:100])

    try: load_security_dataset("delitos_sexuales", "delitos_sexuales_apartado.json", "delitos_sexuales_raw")
    except Exception as e: report("delitos_sexuales", "error", detail=str(e)[:100])

    try: load_security_dataset("violencia_intrafamiliar", "violencia_intrafamiliar_apartado.json", "violencia_intrafamiliar_raw")
    except Exception as e: report("violencia_intrafamiliar", "error", detail=str(e)[:100])

    # Conflicto
    try: load_victimas()
    except Exception as e: report("victimas_conflicto", "error", detail=str(e)[:100])

    # Resumen
    print("\n" + "=" * 70)
    print("  RESUMEN ETL")
    print("=" * 70)
    ok_count = sum(1 for r in results if r["status"] == "ok")
    err_count = sum(1 for r in results if r["status"] == "error")
    total_records = sum(r["registros"] for r in results if r["status"] == "ok")
    print(f"  Exitosos: {ok_count}")
    print(f"  Fallidos: {err_count}")
    print(f"  Total registros cargados: {total_records:,}")
    print("=" * 70)

    # Save report
    report_path = BASE_DIR / "docs" / "etl_report.json"
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Reporte guardado en: {report_path}")


if __name__ == "__main__":
    main()
