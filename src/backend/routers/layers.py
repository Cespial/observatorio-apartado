"""
Gestión de capas — catálogo de todas las capas disponibles
"""
from fastapi import APIRouter
from ..database import engine
from sqlalchemy import text

router = APIRouter(prefix="/api/layers", tags=["Capas"])

# Registro de capas disponibles
LAYERS_CATALOG = [
    {
        "id": "limite_municipal",
        "name": "Límite Municipal",
        "schema": "cartografia",
        "table": "limite_municipal",
        "description": "Polígono del municipio de Apartadó",
        "geometry_type": "Polygon",
        "category": "cartografia",
    },
    {
        "id": "manzanas_censales",
        "name": "Manzanas Censales (MGN 2018)",
        "schema": "cartografia",
        "table": "manzanas_censales",
        "description": "Manzanas del censo 2018 con datos de población",
        "geometry_type": "MultiPolygon",
        "category": "cartografia",
    },
    {
        "id": "igac_apartado",
        "name": "Municipio IGAC",
        "schema": "cartografia",
        "table": "igac_municipios",
        "description": "Polígono oficial IGAC de Apartadó",
        "geometry_type": "MultiPolygon",
        "category": "cartografia",
    },
    {
        "id": "igac_uraba",
        "name": "Municipios de Urabá",
        "schema": "cartografia",
        "table": "igac_uraba",
        "description": "8 municipios de la región de Urabá",
        "geometry_type": "MultiPolygon",
        "category": "cartografia",
    },
    {
        "id": "osm_edificaciones",
        "name": "Edificaciones (OSM)",
        "schema": "cartografia",
        "table": "osm_edificaciones",
        "description": "Edificaciones de OpenStreetMap",
        "geometry_type": "Polygon",
        "category": "osm",
    },
    {
        "id": "osm_vias",
        "name": "Red Vial (OSM)",
        "schema": "cartografia",
        "table": "osm_vias",
        "description": "Vías y calles de OpenStreetMap",
        "geometry_type": "LineString",
        "category": "osm",
    },
    {
        "id": "osm_uso_suelo",
        "name": "Uso del Suelo (OSM)",
        "schema": "cartografia",
        "table": "osm_uso_suelo",
        "description": "Clasificación de uso del suelo OSM",
        "geometry_type": "Polygon",
        "category": "osm",
    },
    {
        "id": "osm_amenidades",
        "name": "Amenidades (OSM)",
        "schema": "cartografia",
        "table": "osm_amenidades",
        "description": "Puntos de interés de OpenStreetMap",
        "geometry_type": "Point",
        "category": "osm",
    },
    {
        "id": "google_places",
        "name": "Negocios y Servicios (Google)",
        "schema": "servicios",
        "table": "google_places",
        "description": "877 establecimientos comerciales de Google Places",
        "geometry_type": "Point",
        "category": "economia",
    },
]


@router.get("")
def list_layers():
    """Listar todas las capas disponibles con conteo de registros."""
    results = []
    for layer in LAYERS_CATALOG:
        try:
            with engine.connect() as conn:
                count = conn.execute(
                    text(f"SELECT COUNT(*) FROM {layer['schema']}.{layer['table']}")
                ).scalar()
        except Exception:
            count = 0
        results.append({**layer, "record_count": count})
    return results


@router.get("/{layer_id}/geojson")
def get_layer_geojson(layer_id: str, limit: int = 5000):
    """Obtener GeoJSON completo de una capa."""
    layer = next((l for l in LAYERS_CATALOG if l["id"] == layer_id), None)
    if not layer:
        return {"error": f"Capa '{layer_id}' no encontrada"}

    import geopandas as gpd
    with engine.connect() as conn:
        gdf = gpd.read_postgis(
            text(f"SELECT * FROM {layer['schema']}.{layer['table']} LIMIT :lim"),
            conn,
            geom_col="geom",
            params={"lim": limit},
        )
    if gdf.empty:
        return {"type": "FeatureCollection", "features": []}
    return eval(gdf.to_json())


@router.get("/{layer_id}/stats")
def get_layer_stats(layer_id: str):
    """Estadísticas básicas de una capa (bbox, conteo, columnas)."""
    layer = next((l for l in LAYERS_CATALOG if l["id"] == layer_id), None)
    if not layer:
        return {"error": f"Capa '{layer_id}' no encontrada"}

    with engine.connect() as conn:
        count = conn.execute(
            text(f"SELECT COUNT(*) FROM {layer['schema']}.{layer['table']}")
        ).scalar()
        bbox = conn.execute(
            text(f"SELECT ST_Extent(geom)::text FROM {layer['schema']}.{layer['table']}")
        ).scalar()
        cols = conn.execute(
            text(
                "SELECT column_name, data_type FROM information_schema.columns "
                "WHERE table_schema = :s AND table_name = :t ORDER BY ordinal_position"
            ),
            {"s": layer["schema"], "t": layer["table"]},
        ).fetchall()

    return {
        "layer_id": layer_id,
        "name": layer["name"],
        "record_count": count,
        "bbox": bbox,
        "columns": [{"name": c[0], "type": c[1]} for c in cols],
    }
