"""
Router para el mercado laboral y ofertas de empleo en Urabá
"""
from fastapi import APIRouter, Query, HTTPException
from ..database import get_sqlite_conn, cached
import pandas as pd

router = APIRouter(prefix="/api/empleo", tags=["Empleo"])

@router.get("/ofertas")
@cached(ttl_seconds=3600)
def get_ofertas(
    municipio: str = Query(None, description="Filtrar por municipio (Apartadó, Turbo, etc)"),
    fuente: str = Query(None, description="Filtrar por fuente (computrabajo, sena, etc)"),
    busqueda: str = Query(None, description="Buscar en título o descripción"),
    limit: int = Query(100, le=1000)
):
    """Listado de ofertas laborales recolectadas por el scraper."""
    conn = get_sqlite_conn()
    query = "SELECT * FROM ofertas WHERE 1=1"
    params = []
    
    if municipio:
        query += " AND municipio LIKE ?"
        params.append(f"%{municipio}%")
    if fuente:
        query += " AND fuente = ?"
        params.append(fuente)
    if busqueda:
        query += " AND (titulo LIKE ? OR descripcion LIKE ?)"
        params.append(f"%{busqueda}%")
        params.append(f"%{busqueda}%")
    
    query += " ORDER BY fecha_scraping DESC LIMIT ?"
    params.append(limit)
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df.to_dict(orient="records")

@router.get("/stats")
@cached(ttl_seconds=3600)
def get_empleo_stats():
    """Estadísticas rápidas del mercado laboral."""
    conn = get_sqlite_conn()
    
    # Ofertas por municipio
    df_muni = pd.read_sql_query(
        "SELECT municipio, COUNT(*) as total FROM ofertas GROUP BY municipio ORDER BY total DESC", 
        conn
    )
    
    # Ofertas por fuente
    df_fuente = pd.read_sql_query(
        "SELECT fuente, COUNT(*) as total FROM ofertas GROUP BY fuente ORDER BY total DESC", 
        conn
    )
    
    # Top empresas
    df_empresa = pd.read_sql_query(
        "SELECT empresa, COUNT(*) as total FROM ofertas WHERE empresa != 'No especificada' GROUP BY empresa ORDER BY total DESC LIMIT 10", 
        conn
    )
    
    conn.close()
    
    return {
        "por_municipio": df_muni.to_dict(orient="records"),
        "por_fuente": df_fuente.to_dict(orient="records"),
        "top_empresas": df_empresa.to_dict(orient="records")
    }

@router.get("/fuentes")
def list_fuentes():
    """Listar fuentes de empleo soportadas."""
    return ["computrabajo", "elempleo", "sena", "linkedin", "comfama", "comfenalco", "indeed"]
