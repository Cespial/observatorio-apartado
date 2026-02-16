from pydantic import BaseModel
from typing import Optional


class LayerInfo(BaseModel):
    id: str
    name: str
    schema_name: str
    table_name: str
    description: str
    geometry_type: str
    record_count: int
    category: str


class IndicatorInfo(BaseModel):
    id: str
    name: str
    description: str
    source: str
    unit: str
    category: str


class CrossVarRequest(BaseModel):
    var_x: str
    var_y: str
    geo_level: Optional[str] = "municipal"


class StatsResponse(BaseModel):
    municipio: str
    divipola: str
    departamento: str
    indicadores: dict
