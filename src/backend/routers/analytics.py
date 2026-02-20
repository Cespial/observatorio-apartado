"""
Módulo de Analítica Avanzada — Inteligencia Territorial para Urabá
"""
from fastapi import APIRouter, Query, HTTPException
from ..database import engine, get_sqlite_conn, cached, query_dicts
from sqlalchemy import text
import pandas as pd
import numpy as np
from typing import List, Optional

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/gaps")
@cached(ttl_seconds=3600)
def get_gaps(
    dane_code: str = Query("05045", description="Código DANE del municipio"),
    indicador: str = Query("Población total", description="Indicador a comparar")
):
    """
    Calcula la brecha (Gap) entre un municipio y el promedio de la subregión de Urabá.
    """
    sql = """
        WITH regional_avg AS (
            SELECT indicador, AVG(dato_numerico) as avg_val, anio
            FROM socioeconomico.terridata
            WHERE indicador = :indicador
            GROUP BY indicador, anio
            ORDER BY anio DESC
            LIMIT 1
        ),
        muni_val AS (
            SELECT entidad, dato_numerico as muni_val, anio
            FROM socioeconomico.terridata
            WHERE indicador = :indicador AND codigo_entidad = :dane_code
            ORDER BY anio DESC
            LIMIT 1
        )
        SELECT 
            m.entidad as municipio,
            m.muni_val as valor_municipio,
            r.avg_val as promedio_regional,
            (m.muni_val - r.avg_val) as brecha_absoluta,
            CASE WHEN r.avg_val != 0 THEN ((m.muni_val - r.avg_val) / r.avg_val) * 100 ELSE 0 END as brecha_porcentual,
            m.anio
        FROM muni_val m, regional_avg r
    """
    results = query_dicts(sql, {"dane_code": dane_code, "indicador": indicador})
    if not results:
        raise HTTPException(status_code=404, detail="No se encontraron datos para el indicador o municipio especificado")
    return results[0]

@router.get("/ranking")
@cached(ttl_seconds=3600)
def get_ranking(
    indicador: str = Query("Población total", description="Indicador para el ranking"),
    order: str = Query("desc", enum=["asc", "desc"])
):
    """
    Genera un ranking de los municipios de Urabá según un indicador de Terridata.
    """
    sql = f"""
        WITH latest_data AS (
            SELECT DISTINCT ON (entidad)
                entidad as municipio,
                codigo_entidad as dane_code,
                dato_numerico as valor,
                anio
            FROM socioeconomico.terridata
            WHERE indicador = :indicador
            ORDER BY entidad, anio DESC
        )
        SELECT * FROM latest_data
        ORDER BY valor {order}
    """
    return query_dicts(sql, {"indicador": indicador})

@router.get("/laboral/termometro")
@cached(ttl_seconds=3600)
def get_termometro_laboral():
    """
    Termómetro Laboral: Intensidad de ofertas laborales recientes por municipio.
    """
    conn = get_sqlite_conn()
    # Ofertas en los últimos 7 días vs los 7 días anteriores
    query = """
        SELECT 
            municipio,
            COUNT(CASE WHEN date(fecha_scraping) >= date('now', '-7 days') THEN 1 END) as ultimos_7_dias,
            COUNT(CASE WHEN date(fecha_scraping) < date('now', '-7 days') AND date(fecha_scraping) >= date('now', '-14 days') THEN 1 END) as anteriores_7_dias
        FROM ofertas
        GROUP BY municipio
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Calcular tendencia
    df['tendencia'] = ((df['ultimos_7_dias'] - df['anteriores_7_dias']) / df['anteriores_7_dias'].replace(0, 1)) * 100
    return df.to_dict(orient="records")

@router.get("/laboral/oferta-demanda")
@cached(ttl_seconds=3600)
def get_oferta_demanda():
    """
    Análisis de Oferta (Scraper) vs Demanda Potencial (Población en edad de trabajar).
    Nota: La demanda se estima con la población de Terridata si está disponible.
    """
    # 1. Obtener oferta desde SQLite
    conn = get_sqlite_conn()
    df_oferta = pd.read_sql_query(
        "SELECT municipio, COUNT(*) as vacantes FROM ofertas GROUP BY municipio", conn
    )
    conn.close()
    
    # 2. Obtener población (demanda proxy) desde PostgreSQL
    # Usamos 'Población total' como proxy si no hay dato exacto de PET
    sql_pop = """
        SELECT entidad as municipio, dato_numerico as poblacion
        FROM socioeconomico.terridata
        WHERE indicador = 'Población total'
        AND anio = (SELECT MAX(anio) FROM socioeconomico.terridata WHERE indicador = 'Población total')
    """
    df_pop = pd.DataFrame(query_dicts(sql_pop))
    
    if df_pop.empty:
        return {"error": "No se encontraron datos de población para el análisis"}
        
    # Merge y cálculo de ratio
    # Normalizar nombres de municipios para el merge
    df_oferta['municipio_key'] = df_oferta['municipio'].str.lower().str.strip()
    df_pop['municipio_key'] = df_pop['municipio'].str.lower().str.strip()
    
    df_merged = pd.merge(df_oferta, df_pop, on='municipio_key', suffixes=('_oferta', '_pop'))
    df_merged['vacantes_por_1000_hab'] = (df_merged['vacantes'] / df_merged['poblacion']) * 1000
    
    return df_merged[['municipio_pop', 'vacantes', 'poblacion', 'vacantes_por_1000_hab']].to_dict(orient="records")

@router.get("/clusters")
@cached(ttl_seconds=3600)
def get_territorial_clusters():
    """
    Agrupamiento de municipios por similitud socioeconómica.
    Utiliza un enfoque de reglas lógicas para definir perfiles territoriales.
    """
    # Traemos indicadores clave para clustering
    sql = """
        SELECT 
            entidad as municipio,
            indicador,
            dato_numerico as valor
        FROM socioeconomico.terridata
        WHERE indicador IN ('Población total', 'Incidencia de la pobreza monetaria', 'Valor agregado municipal')
        AND anio = (SELECT MAX(anio) FROM socioeconomico.terridata)
    """
    data = query_dicts(sql)
    if not data:
        return {"error": "Datos insuficientes para clustering"}
        
    df = pd.DataFrame(data).pivot(index='municipio', columns='indicador', values='valor').reset_index()
    
    clusters = []
    for _, row in df.iterrows():
        # Lógica de clustering (Reglas de negocio regional)
        poblacion = row.get('Población total', 0)
        pobreza = row.get('Incidencia de la pobreza monetaria', 0)
        pib = row.get('Valor agregado municipal', 0)
        
        if poblacion > 100000:
            cluster = "Nodo Urbano Regional"
            desc = "Municipios con alta densidad poblacional y servicios centralizados."
        elif pib > 1000000: # Ejemplo de umbral
            cluster = "Eje Agroindustrial"
            desc = "Municipios con fuerte base económica en banano/plátano y logística."
        elif pobreza > 50:
            cluster = "Territorio en Desarrollo"
            desc = "Municipios con altos retos sociales y brechas de infraestructura."
        else:
            cluster = "Ruralidad Emergente"
            desc = "Municipios con economías en transición y potencial turístico."
            
        clusters.append({
            "municipio": row['municipio'],
            "cluster": cluster,
            "descripcion": desc,
            "indicadores": {
                "poblacion": poblacion,
                "pobreza": pobreza,
                "pib": pib
            }
        })
        
    return clusters
