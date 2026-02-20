# Observatorio Regional de Urabá

Plataforma integral de inteligencia territorial para la subregión de Urabá, Antioquia. Integra datos geoespaciales, socioeconómicos, de seguridad, salud, educación, economía, gobernanza y mercado laboral para los 11 municipios de la región.

## 📌 Identidad Regional
Este proyecto ha evolucionado de un enfoque local en Apartadó a una visión regional integral que abarca:
- **Eje Bananero:** Apartadó, Carepa, Chigorodó, Mutatá.
- **Distrito & Costa:** Turbo (Distrito Portuario), Necoclí, San Pedro de Urabá, San Juan de Urabá, Arboletes.
- **Atrato Medio:** Murindó, Vigía del Fuerte.

## 🛠 Arquitectura Técnica
- **Backend:** FastAPI (Python) + SQLAlchemy (PostgreSQL/PostGIS).
- **Frontend:** React + Vite + Deck.gl + MapLibre GL (Venta de mapas y capas).
- **ETL:** Pipelines en Python para limpieza y normalización de fuentes oficiales (DANE, DNP, Policía, etc.).
- **Infraestructura:** Despliegue en Vercel (API y Frontend) + Base de Datos gestionada.

## 📂 Estructura del Proyecto
- `/api`: Entry points para Vercel.
- `/src/backend`: Lógica central del API, modelos y routers.
- `/src/frontend`: Aplicación web interactiva.
- `/etl`: Scripts de extracción, transformación y carga de datos.
- `/docs`: Documentación técnica y reportes de datos.
- `/data`: Almacenamiento local de archivos procesados y volcados de DB.

## 🚀 Inicio Rápido
1. Clone el repositorio.
2. Configure su archivo `.env` con las credenciales de PostgreSQL/PostGIS.
3. Instale dependencias: `pip install -r requirements.txt`.
4. Ejecute el backend: `python src/backend/main.py`.
5. En otra terminal, instale dependencias de frontend: `npm install` dentro de `src/frontend`.

## 📖 Documentación Adicional
- [Diccionario de Datos (DATA_DICTIONARY.md)](DATA_DICTIONARY.md)
- [Guía de Contribución (CONTRIBUTING.md)](CONTRIBUTING.md)
- [Reportes de Calidad de Datos](docs/etl_report.json)
