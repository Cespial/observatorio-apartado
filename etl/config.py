# Configuration for Urabá Regional Observatory
import os

MUNICIPIOS = [
    ("05045", "Apartadó",   [-76.80, 7.70, -76.35, 8.10]),
    ("05051", "Arboletes",  [-76.60, 8.70, -76.20, 9.10]),
    ("05147", "Carepa",     [-76.80, 7.60, -76.40, 7.95]),
    ("05172", "Chigorodó",  [-76.85, 7.50, -76.30, 7.85]),
    ("05475", "Murindó",    [-77.00, 6.80, -76.50, 7.20]),
    ("05480", "Mutatá",     [-76.60, 7.10, -76.20, 7.50]),
    ("05490", "Necoclí",    [-77.00, 8.30, -76.50, 8.70]),
    ("05659", "San Juan",   [-76.70, 8.80, -76.30, 9.20]),
    ("05665", "San Pedro",  [-76.50, 8.10, -76.10, 8.50]),
    ("05837", "Turbo",      [-77.10, 7.90, -76.40, 8.60]),
    ("05873", "Vigía",      [-77.10, 6.40, -76.40, 7.00])
]

URABA_DANE_CODES = [m[0] for m in MUNICIPIOS]

DB_URL = os.getenv("DATABASE_URL", "postgresql://cristianespinal@localhost:5433/observatorio_apartado")
