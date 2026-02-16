import json
import time
from functools import wraps
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
)


_cache = {}


def cached(ttl_seconds: int = 300):
    """Simple in-memory TTL cache decorator for endpoint functions."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            key = (fn.__name__, args, tuple(sorted(kwargs.items())))
            entry = _cache.get(key)
            if entry and time.time() - entry[0] < ttl_seconds:
                return entry[1]
            result = fn(*args, **kwargs)
            _cache[key] = (time.time(), result)
            return result
        return wrapper
    return decorator
SessionLocal = sessionmaker(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def query_dicts(sql: str, params: dict = None) -> list[dict]:
    """Execute SQL once and return list of dicts."""
    with engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        columns = list(result.keys())
        return [dict(zip(columns, row)) for row in result.fetchall()]


def query_df(sql: str, params: dict = None):
    """Execute SQL and return pandas DataFrame."""
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
    return json.loads(gdf.to_json())
