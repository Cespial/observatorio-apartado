#!/usr/bin/env python3
"""
ETL 13 — Backfill enrichment fields on existing offers
=======================================================
One-off script that reads all existing offers from PG and applies
the new NLP extractors (experiencia, contrato, educacion, modalidad)
plus expanded skill patterns, updating each row in batch.

Usage:
  python etl/13_backfill_enrichment.py
"""

import sys
import re
from pathlib import Path
from sqlalchemy import create_engine, text

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import DB_URL

# Import patterns from ETL 12 to stay DRY
sys.path.insert(0, str(Path(__file__).resolve().parent))

SKILL_PATTERNS = [
    (r'\bexcel\b', 'Excel'),
    (r'\bword\b', 'Word'),
    (r'\bsap\b', 'SAP'),
    (r'\bpython\b', 'Python'),
    (r'\bsql\b', 'SQL'),
    (r'\bingl[eé]s\b', 'Inglés'),
    (r'\bcontabilidad\b', 'Contabilidad'),
    (r'\bfacturaci[oó]n\b', 'Facturación'),
    (r'\batenci[oó]n al cliente\b', 'Atención al cliente'),
    (r'\bservicio al cliente\b', 'Servicio al cliente'),
    (r'\bventas\b', 'Ventas'),
    (r'\bliderazgo\b', 'Liderazgo'),
    (r'\btrabajo en equipo\b', 'Trabajo en equipo'),
    (r'\bcomunicaci[oó]n\b', 'Comunicación'),
    (r'\bnegociaci[oó]n\b', 'Negociación'),
    (r'\bmanejo de personal\b', 'Manejo de personal'),
    (r'\blogística\b|\blogistica\b', 'Logística'),
    (r'\bpresupuesto\b', 'Presupuesto'),
    (r'\bmarketing\b|\bmercadeo\b', 'Marketing'),
    (r'\bredes sociales\b|\bsocial media\b', 'Redes sociales'),
    (r'\blicencia\s+(de\s+)?conducci[oó]n\b|\blicencia\s+[bc]\d\b', 'Licencia de conducción'),
    (r'\bmoto\b', 'Moto propia'),
    (r'\bsalud ocupacional\b|\bsst\b|\bseguridad y salud\b', 'SST'),
    (r'\bagricultura\b|\bagrícola\b|\bagricola\b|\bcultivo\b', 'Agricultura'),
    (r'\bbanano\b|\bplátano\b|\bplatano\b', 'Cultivo banano/plátano'),
    (r'\bglobalg\.?a\.?p\.?\b|\brainforest\b', 'Certificaciones agrícolas'),
    (r'\benfermería\b|\benfermeria\b|\benfermero\b', 'Enfermería'),
    (r'\bmedicina\b|\bmédico\b|\bmedico\b', 'Medicina'),
    (r'\bpedagog\b|\beducaci[oó]n\b|\bdocente\b|\bprofesor\b', 'Educación'),
    (r'\bconstrucci[oó]n\b|\bobra\b|\bingeniería civil\b', 'Construcción'),
    (r'\belectricidad\b|\beléctric\b|\belectric\b', 'Electricidad'),
    (r'\bmecánic\b|\bmecanica\b', 'Mecánica'),
    (r'\bsoldadura\b', 'Soldadura'),
    # Herramientas y Software
    (r'\bpower\s*bi\b', 'Power BI'),
    (r'\btableau\b', 'Tableau'),
    (r'\berp\b', 'ERP'),
    (r'\bcrm\b', 'CRM'),
    (r'\bautocad\b|\bauto\s*cad\b', 'AutoCAD'),
    (r'\bphotoshop\b|\billustrator\b|\bdise[nñ]o\b', 'Diseno grafico'),
    (r'\bsiigo\b|\bworld\s*office\b|\bhelisa\b', 'Software contable'),
    # Habilidades blandas y gestion
    (r'\bplaneaci[oó]n\b|\bplanificaci[oó]n\b', 'Planeacion'),
    (r'\bgesti[oó]n\b', 'Gestion'),
    (r'\binventario\b', 'Inventarios'),
    (r'\bcaja\b|\bmanejo.*efectivo\b', 'Manejo de caja'),
    (r'\bcobranza\b|\bcartera\b', 'Cobranza/Cartera'),
    (r'\bimportaci[oó]n\b|\bexportaci[oó]n\b|\bcomercio\s+exterior\b', 'Comercio exterior'),
    (r'\bcalidad\b|\biso\b|\bnormas?\b', 'Gestion de calidad'),
    (r'\bprimeros\s+auxilios\b|\bbrigad\b', 'Primeros auxilios'),
    # Agro-especificos de Uraba
    (r'\bfitosanitar\b|\bplagas?\b|\bfumig\b', 'Fitosanidad'),
    (r'\bempaque\b|\bembalaje\b|\bempacad\b', 'Empaque'),
    (r'\bcosecha\b|\brecolec\b|\bcorte\b.*\bbanano\b', 'Cosecha'),
    (r'\briego\b|\bdrenaje\b|\bfertirriego\b', 'Riego y drenaje'),
    (r'\bcertific\b.*\borganic\b|\bglobal\s*gap\b', 'Certificacion organica'),
    # Transporte y operaciones
    (r'\bmontacarga\b', 'Montacargas'),
    (r'\bveh[ií]culo\s+propio\b', 'Vehiculo propio'),
    (r'\bcadena\s+de\s+fr[ií]o\b', 'Cadena de frio'),
    (r'\bBPM\b|\bbuenas\s+pr[aá]cticas\b', 'BPM'),
    (r'\bHACCP\b', 'HACCP'),
]

EXPERIENCIA_PATTERNS = [
    (r'sin\s+experiencia|no\s+requiere\s+experiencia|primera\s+vez', 'Sin experiencia'),
    (r'1\s*a[nñ]o|12\s*meses|un\s*\(?\d?\)?\s*a[nñ]o', '1 ano'),
    (r'2\s*a[nñ]os?|24\s*meses', '2 anos'),
    (r'3\s*a[nñ]os?|36\s*meses', '3 anos'),
    (r'[45]\s*a[nñ]os?', '4-5 anos'),
    (r'[6-9]\s*a[nñ]os?|\d{2,}\s*a[nñ]os?|m[aá]s\s+de\s+5', '5+ anos'),
]

CONTRATO_PATTERNS = [
    (r'indefinido|fijo\s+indefinido|planta', 'Indefinido'),
    (r'fijo|t[eé]rmino\s+fijo|temporal', 'Fijo'),
    (r'prestaci[oó]n\s+de\s+servicios|contratista|independiente|freelance', 'Prestacion de servicios'),
    (r'obra\s+o?\s*labor|obra\s+civil|por\s+obra', 'Obra o labor'),
    (r'aprendiz|sena|practicante|pr[aá]ctica', 'Aprendizaje'),
]

EDUCACION_PATTERNS = [
    (r'bachiller|secundaria|11[°º]', 'Bachiller'),
    (r't[eé]cnic[oa]', 'Tecnico'),
    (r'tecn[oó]log[oa]', 'Tecnologo'),
    (r'profesional|universitari[oa]|ingenier[oa]|abogad[oa]|licenciad[oa]', 'Profesional'),
    (r'especializaci[oó]n|especialista|postgrado|posgrado', 'Especializacion'),
    (r'maestr[ií]a|magister|m[aá]ster', 'Maestria'),
]

MODALIDAD_PATTERNS = [
    (r'remoto|teletrabajo|home\s*office|desde\s+casa|virtual', 'Remoto'),
    (r'h[ií]brido|mixto|alterno', 'Hibrido'),
    (r'presencial|en\s+sitio|campo|planta', 'Presencial'),
]


def extract_skills(titulo, descripcion):
    combined = f"{titulo or ''} {descripcion or ''}".lower()
    return [name for pattern, name in SKILL_PATTERNS if re.search(pattern, combined, re.IGNORECASE)]


def extract_enrichment(titulo, descripcion):
    combined = f"{titulo or ''} {descripcion or ''}".lower()
    result = {}
    for patterns, key in [
        (EXPERIENCIA_PATTERNS, 'nivel_experiencia'),
        (CONTRATO_PATTERNS, 'tipo_contrato'),
        (EDUCACION_PATTERNS, 'nivel_educativo'),
        (MODALIDAD_PATTERNS, 'modalidad'),
    ]:
        for pattern, label in patterns:
            if re.search(pattern, combined, re.IGNORECASE):
                result[key] = label
                break
        else:
            result[key] = None
    return result


def main():
    engine = create_engine(DB_URL, pool_size=1, max_overflow=0)

    # Ensure columns exist
    with engine.begin() as conn:
        for col in ['nivel_experiencia', 'tipo_contrato', 'nivel_educativo', 'modalidad']:
            conn.execute(text(f"ALTER TABLE empleo.ofertas_laborales ADD COLUMN IF NOT EXISTS {col} TEXT"))

    # Read all offers
    with engine.connect() as conn:
        rows = conn.execute(text(
            "SELECT id, titulo, descripcion FROM empleo.ofertas_laborales ORDER BY id"
        )).fetchall()

    print(f"Total ofertas a procesar: {len(rows)}")

    updated = 0
    batch_size = 500
    updates = []

    for row in rows:
        oid, titulo, desc = row[0], row[1], row[2]
        skills = extract_skills(titulo, desc)
        enrich = extract_enrichment(titulo, desc)
        updates.append({
            "oid": oid,
            "skills": skills,
            "nivel_experiencia": enrich['nivel_experiencia'],
            "tipo_contrato": enrich['tipo_contrato'],
            "nivel_educativo": enrich['nivel_educativo'],
            "modalidad": enrich['modalidad'],
        })

        if len(updates) >= batch_size:
            with engine.begin() as conn:
                for u in updates:
                    conn.execute(text("""
                        UPDATE empleo.ofertas_laborales
                        SET skills = :skills,
                            nivel_experiencia = :nivel_experiencia,
                            tipo_contrato = :tipo_contrato,
                            nivel_educativo = :nivel_educativo,
                            modalidad = :modalidad
                        WHERE id = :oid
                    """), u)
            updated += len(updates)
            print(f"  Actualizadas: {updated}/{len(rows)}")
            updates = []

    # Flush remaining
    if updates:
        with engine.begin() as conn:
            for u in updates:
                conn.execute(text("""
                    UPDATE empleo.ofertas_laborales
                    SET skills = :skills,
                        nivel_experiencia = :nivel_experiencia,
                        tipo_contrato = :tipo_contrato,
                        nivel_educativo = :nivel_educativo,
                        modalidad = :modalidad
                    WHERE id = :oid
                """), u)
        updated += len(updates)

    print(f"\nBackfill completado: {updated} ofertas enriquecidas")

    # Summary
    with engine.connect() as conn:
        for col in ['nivel_experiencia', 'tipo_contrato', 'nivel_educativo', 'modalidad']:
            count = conn.execute(text(
                f"SELECT COUNT(*) FROM empleo.ofertas_laborales WHERE {col} IS NOT NULL"
            )).scalar()
            print(f"  {col}: {count} ofertas con valor")

    engine.dispose()


if __name__ == "__main__":
    main()
