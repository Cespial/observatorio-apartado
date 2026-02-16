from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def query_df(sql: str, params: dict = None):
    """Execute SQL and return list of dicts."""
    import pandas as pd
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn, params=params)
    return df


def query_geojson(sql: str, params: dict = None) -> dict:
    """Execute SQL that returns geometry and build a GeoJSON FeatureCollection."""
    import geopandas as gpd
    with engine.connect() as conn:
        gdf = gpd.read_postgis(text(sql), conn, geom_col="geom", params=params)
    if gdf.empty:
        return {"type": "FeatureCollection", "features": []}
    return eval(gdf.to_json())
