#!/usr/bin/env python3
"""
Google Places API — Descargar negocios y POIs de Apartadó
Usa la API Nearby Search para mapear la economía local
"""
import json
import os
import time
from pathlib import Path

import requests
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
DB_URL = os.getenv("DATABASE_URL")
engine = create_engine(DB_URL)

# Centro de Apartadó
APARTADO_LAT = 7.8833
APARTADO_LNG = -76.6258

# Categorías a buscar
CATEGORIES = [
    ("restaurant", "Restaurantes"),
    ("bank", "Bancos"),
    ("pharmacy", "Farmacias"),
    ("hospital", "Hospitales"),
    ("school", "Colegios"),
    ("supermarket", "Supermercados"),
    ("gas_station", "Estaciones de servicio"),
    ("store", "Tiendas"),
    ("church", "Iglesias"),
    ("hotel", "Hoteles"),
    ("gym", "Gimnasios"),
    ("cafe", "Cafeterías"),
    ("bar", "Bares"),
    ("bakery", "Panaderías"),
    ("hardware_store", "Ferreterías"),
    ("clothing_store", "Tiendas de ropa"),
    ("beauty_salon", "Salones de belleza"),
    ("car_repair", "Talleres mecánicos"),
    ("dentist", "Dentistas"),
    ("veterinary_care", "Veterinarias"),
    ("laundry", "Lavanderías"),
    ("atm", "Cajeros automáticos"),
]

OUTPUT_DIR = BASE_DIR / "data" / "google_places"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def search_nearby(lat, lng, place_type, radius=5000):
    """Buscar lugares cercanos usando Nearby Search API"""
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    all_results = []
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "type": place_type,
        "key": API_KEY,
        "language": "es",
    }

    while True:
        resp = requests.get(url, params=params, timeout=30)
        data = resp.json()

        if data.get("status") not in ("OK", "ZERO_RESULTS"):
            print(f"    API Error: {data.get('status')} - {data.get('error_message', '')}")
            break

        all_results.extend(data.get("results", []))

        # Paginación
        next_token = data.get("next_page_token")
        if not next_token:
            break

        time.sleep(2)  # Google requiere esperar para next_page_token
        params = {"pagetoken": next_token, "key": API_KEY}

    return all_results


def process_results(results, category_name):
    """Procesar resultados de la API a formato limpio"""
    places = []
    for r in results:
        loc = r.get("geometry", {}).get("location", {})
        places.append({
            "place_id": r.get("place_id"),
            "name": r.get("name"),
            "category": category_name,
            "types": r.get("types", []),
            "address": r.get("vicinity"),
            "rating": r.get("rating"),
            "user_ratings_total": r.get("user_ratings_total"),
            "price_level": r.get("price_level"),
            "lat": loc.get("lat"),
            "lon": loc.get("lng"),
        })
    return places


def load_to_db(all_places):
    """Cargar todos los lugares a PostGIS"""
    if not all_places:
        print("  Sin datos para cargar")
        return

    from shapely.geometry import Point
    import geopandas as gpd

    for p in all_places:
        if p["lat"] and p["lon"]:
            p["geom"] = Point(p["lon"], p["lat"])
        else:
            p["geom"] = None
        p["types"] = json.dumps(p["types"])

    gdf = gpd.GeoDataFrame(all_places, geometry="geom", crs="EPSG:4326")
    gdf = gdf[gdf.geom.notna()]

    # Deduplicar por place_id
    gdf = gdf.drop_duplicates(subset=["place_id"])

    gdf.to_postgis("google_places", engine, schema="servicios", if_exists="replace", index=False)
    print(f"\n  Cargados {len(gdf)} lugares a PostGIS")


def main():
    print("=" * 60)
    print("  GOOGLE PLACES API — APARTADÓ")
    print("=" * 60)

    if not API_KEY:
        print("  ERROR: GOOGLE_MAPS_API_KEY no configurada en .env")
        return

    all_places = []

    for place_type, label in CATEGORIES:
        print(f"  Buscando: {label} ({place_type})...")
        results = search_nearby(APARTADO_LAT, APARTADO_LNG, place_type)
        places = process_results(results, label)
        all_places.extend(places)
        print(f"    -> {len(places)} resultados")

        # Guardar JSON individual
        with open(OUTPUT_DIR / f"{place_type}.json", "w") as f:
            json.dump(places, f, indent=2, ensure_ascii=False)

        time.sleep(0.5)  # Rate limiting

    # Guardar JSON consolidado
    with open(OUTPUT_DIR / "all_places.json", "w") as f:
        json.dump(all_places, f, indent=2, ensure_ascii=False)

    print(f"\n  Total lugares encontrados: {len(all_places)}")

    # Cargar a PostGIS
    load_to_db(all_places)

    # Estadísticas por categoría
    print("\n  RESUMEN POR CATEGORÍA:")
    from collections import Counter
    cats = Counter(p["category"] for p in all_places)
    for cat, count in cats.most_common():
        print(f"    {cat}: {count}")

    print("=" * 60)


if __name__ == "__main__":
    main()
