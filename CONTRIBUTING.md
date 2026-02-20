# Guía de Contribución: Añadir un Nuevo Municipio (Urabá)

Este documento detalla los pasos técnicos necesarios para integrar un nuevo municipio de la subregión de Urabá al Observatorio. El proceso abarca desde la base de datos hasta la visualización en el frontend.

---

## 🏗️ 1. Base de Datos (PostgreSQL / PostGIS)

### 1.1 Esquemas y Datos Regionales
El observatorio utiliza el **Marco Geoestadístico Nacional (MGN)** del DANE. Para añadir un nuevo municipio:
1. Asegúrese de que el esquema `cartografia` contiene las manzanas y áreas urbanas del nuevo municipio.
2. Identifique el **DANE CODE (5 dígitos)**:
   - Apartadó: `05045`
   - Turbo: `05837`
   - Carepa: `05147`
   - Chigorodó: `05172`
   - *Próximos:* Mutatá (`05480`), Necoclí (`05490`), etc.

### 1.2 Importación de Datos Crudos
Para cada nueva fuente de datos (ej: `seguridad.homicidios_raw`), el campo `municipio` o `dane_code` debe coincidir con el código oficial para que las consultas parametrizadas funcionen correctamente.

---

## 🐍 2. Backend (FastAPI)

### 2.1 Actualización de Routers
La mayoría de los endpoints en `src/backend/routers/indicators.py` y `geo.py` ya soportan filtrado por `dane_code`. Si añade un nuevo municipio:
1. Verifique que las consultas SQL incluyan la condición `WHERE municipio = :m` o `WHERE dane_code = :c`.
2. Actualice el endpoint raíz (`/`) en `src/backend/main.py` para incluir el nuevo municipio en el catálogo de respuesta.

### 2.2 Validación de Datos
Utilice los modelos de Pydantic en `src/backend/models` para asegurar que el nuevo municipio cumpla con los esquemas de datos esperados.

---

## 📥 3. Proceso ETL (Data Pipeline)

### 3.1 Scripts de Extracción
Ubicados en `/etl`, los scripts deben actualizarse para incluir el nuevo código DANE:
1. **DNP (TerriData):** Ejecute el script de descarga pasando el código DANE del nuevo municipio como parámetro.
2. **ICFES:** El scraper debe filtrar por el código de departamento `05` (Antioquia) y luego filtrar localmente por municipio.
3. **Scrapers de Empleo:** Añada la palabra clave del municipio a la lista de búsqueda en `etl/scrapers/`.

---

## 🎨 4. Frontend (React / Deck.gl)

### 4.1 Configuración de Vista Inicial
Ubicado en `src/frontend/config.js` (o similar):
1. Añada las coordenadas de centroide (`lat`, `lng`) y el nivel de `zoom` inicial para el nuevo municipio.
2. Actualice el selector de municipios (`MunicipalitySelector`) para incluir la nueva opción y su `dane_code`.

### 4.2 Capas de Mapas
Asegúrese de que el backend sirve los GeoJSON del nuevo municipio a través de `/api/geo/manzanas?dane_code=XXXXX`. El frontend cargará automáticamente la geometría si el selector está bien configurado.

---

## 🧪 5. Validación y Calidad
1. **Ejecute Tests:** `pytest tests/` (si están disponibles).
2. **Verifique `/docs`:** Asegúrese de que el nuevo municipio aparece en los ejemplos de los endpoints.
3. **Reporte de Calidad:** Revise `docs/etl_report.json` para confirmar que los datos del nuevo municipio fueron cargados sin errores de integridad.

---

**Nota:** Si el nuevo municipio requiere una fuente de datos única (ej: una Secretaría de Salud propia), documente el proceso en el `README.md` de la carpeta `etl/`.
