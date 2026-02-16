"""
Observatorio de Ciudades — Apartadó, Antioquia
API Backend (FastAPI)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import layers, geo, indicators, crossvar, stats

TAGS_METADATA = [
    {"name": "Root", "description": "Health check y catálogo de endpoints"},
    {"name": "Capas", "description": "Catálogo de capas geoespaciales, GeoJSON y estadísticas"},
    {"name": "Geo", "description": "Datos geoespaciales filtrados: manzanas, edificaciones, vías, negocios, amenidades"},
    {"name": "Indicadores", "description": "Indicadores socioeconómicos, educativos, de seguridad, salud, economía y gobierno"},
    {"name": "Cruce de Variables", "description": "Análisis multivariado: scatter, correlación, series temporales"},
    {"name": "Estadísticas", "description": "Resumen ejecutivo y catálogo de datos"},
]

app = FastAPI(
    title="Observatorio de Ciudades — Apartadó",
    description=(
        "## API de datos territoriales\n\n"
        "Integra información geoespacial, socioeconómica, de seguridad, salud, "
        "educación, economía y gobernanza del municipio de **Apartadó, Antioquia** "
        "(DANE 05045), región de Urabá.\n\n"
        "### Fuentes de datos\n"
        "- **DANE**: Censo 2018, MGN, proyecciones poblacionales\n"
        "- **DNP**: TerriData (800+ indicadores municipales)\n"
        "- **ICFES**: Saber 11 resultados por colegio\n"
        "- **Policía Nacional**: Homicidios, hurtos, delitos sexuales, VIF\n"
        "- **Unidad de Víctimas**: Víctimas del conflicto armado\n"
        "- **INS**: SIVIGILA eventos epidemiológicos, IRCA calidad del agua\n"
        "- **MinTIC**: Internet fijo, índice de gobierno digital\n"
        "- **SECOP II**: Contratación pública\n"
        "- **MinCIT**: Registro Nacional de Turismo\n"
        "- **Google Places API**: Establecimientos comerciales\n"
        "- **OpenStreetMap**: Edificaciones, vías, amenidades\n\n"
        "### Base de datos\n"
        "**55 tablas** · **123,270 registros** · PostgreSQL + PostGIS 3.6\n\n"
        "### Frontend\n"
        "React 18 + Deck.gl + MapLibre GL + Recharts → `http://localhost:3000`"
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=TAGS_METADATA,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(layers.router)
app.include_router(geo.router)
app.include_router(indicators.router)
app.include_router(crossvar.router)
app.include_router(stats.router)


@app.get("/", tags=["Root"])
def root():
    """Health check y catálogo de endpoints principales."""
    return {
        "name": "Observatorio de Ciudades — Apartadó",
        "version": "2.0.0",
        "municipio": "Apartadó",
        "departamento": "Antioquia",
        "dane_code": "05045",
        "database": {
            "tables": 55,
            "records": 123270,
            "schemas": ["cartografia", "socioeconomico", "seguridad", "servicios"],
        },
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "layers": "/api/layers",
            "geo": "/api/geo/manzanas",
            "indicators": "/api/indicators",
            "crossvar": "/api/crossvar/variables",
            "stats": "/api/stats/summary",
            "catalog": "/api/stats/data-catalog",
            "terridata": "/api/indicators/terridata?dimension=Salud",
            "salud_irca": "/api/indicators/salud/irca",
            "salud_sivigila": "/api/indicators/salud/sivigila/resumen",
            "economia_internet": "/api/indicators/economia/internet/serie",
            "economia_secop": "/api/indicators/economia/secop",
            "economia_turismo": "/api/indicators/economia/turismo",
            "gobierno_finanzas": "/api/indicators/gobierno/finanzas",
            "gobierno_desempeno": "/api/indicators/gobierno/desempeno",
            "gobierno_digital": "/api/indicators/gobierno/digital",
            "gobierno_pobreza": "/api/indicators/gobierno/pobreza",
        },
    }
