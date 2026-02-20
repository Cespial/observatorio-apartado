# DevOps Strategy: Regional Containerization for Observatorio de Ciudades
# Optimized for Geospatial Data (GDAL/PostGIS) and High Performance

FROM python:3.11-slim-bullseye as builder

# Install system dependencies for GDAL and PostGIS
RUN apt-get update && apt-get install -y --no-install-recommends 
    build-essential 
    libpq-dev 
    gdal-bin 
    libgdal-dev 
    python3-gdal 
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for GDAL
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Final Stage
FROM python:3.11-slim-bullseye

RUN apt-get update && apt-get install -y --no-install-recommends 
    libpq5 
    gdal-bin 
    libgdal-dev 
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /install /usr/local
COPY . .

# Environment configuration for Regional Scopes
# Default to Apartadó (05045) but allow multi-municipality expansion
ENV ALLOWED_MUNICIPALITIES="05045"
ENV GEOSPATIAL_SIMPLIFICATION_TOLERANCE="0.0001"
ENV DB_POOL_SIZE="20"
ENV DB_MAX_OVERFLOW="10"

# Expose port for FastAPI
EXPOSE 8000

# Optimization for production
CMD ["uvicorn", "api.index:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
