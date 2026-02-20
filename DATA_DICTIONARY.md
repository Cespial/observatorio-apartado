# Diccionario de Datos Regional (Urabá)

Este documento detalla los indicadores disponibles para los 11 municipios de la subregión de Urabá, Antioquia.

## 📊 Matriz de Disponibilidad de Indicadores por Municipio

| Categoría | Indicador | Apartadó | Turbo | Carepa | Chigorodó | Necoclí | Mutatá | Arboletes | S. Pedro | S. Juan | Vigía | Murindó |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Educación** | Puntaje ICFES (Promedio) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Educación** | Establecimientos (DANE) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Seguridad** | Homicidios / Hurtos | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Seguridad** | Delitos Sexuales / VIF | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Conflicto** | Víctimas del Conflicto | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Salud** | IPS Habilitadas (REPS) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Salud** | IRCA (Calidad de Agua) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Salud** | SIVIGILA (Epidemiología) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Economía** | Internet Fijo (MinTIC) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Economía** | Contratación SECOP II | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Economía** | Turismo (RNT) | ✅ | ✅ | ✅ | ⚠️ | ✅ | ⚠️ | ✅ | ⚠️ | ⚠️ | ❌ | ❌ |
| **Gobernanza** | TerriData (DNP) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Gobernanza** | Gobierno Digital | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Geospatial** | Manzanas (Censo 2018) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Mercado** | Ofertas Empleo (Scrapers) | ✅ | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ❌ | ❌ |

**Leyenda:**
- ✅ **Totalmente Disponible:** Datos actualizados y procesados.
- ⚠️ **Parcialmente Disponible:** Datos con brechas temporales o cobertura geográfica limitada.
- ❌ **No Disponible:** Datos no capturados o no generados por la fuente oficial para ese municipio.

---

## 🏗️ Fuentes de Datos Principales

### 1. Nivel Nacional (DANE / DNP / Ministerios)
- **DANE:** Microdatos del Censo 2018, Marco Geoestadístico Nacional (MGN) y Proyecciones Poblacionales 2018-2050.
- **DNP (TerriData):** Más de 800 indicadores municipales agrupados en dimensiones (Salud, Educación, Finanzas, Pobreza).
- **ICFES:** Resultados agregados y a nivel de estudiante (Saber 11) descargados de `datos.gov.co`.
- **MinTIC:** Datos de penetración de Internet y telefonía móvil por municipio.
- **SECOP II:** Contratación pública detallada (valores, tipos, contratistas).

### 2. Seguridad y Orden Público
- **Policía Nacional (DIJIN):** Casos de delitos registrados en el SIEDCO (Homicidios, Hurtos, Lesiones, VIF).
- **Unidad para las Víctimas:** Registro Único de Víctimas (RUV) anonimizado a nivel municipal.

### 3. Salud y Servicios
- **INS (SIVIGILA):** Notificaciones de eventos de interés en salud pública.
- **MinSalud (REPS):** Registro Especial de Prestadores de Servicios de Salud.
- **INS (IRCA):** Reportes de vigilancia de calidad de agua para consumo humano.

### 4. Fuentes No Estructuradas / Scrapers
- **Google Places API:** Geo-referenciación de establecimientos comerciales y puntos de interés.
- **OpenStreetMap (OSM):** Huellas de edificaciones, red vial y equipamientos urbanos.
- **Scrapers de Empleo:** Datos diarios de portales como Computrabajo, El Empleo y LinkedIn procesados por el módulo `api/routers/empleo.py`.
