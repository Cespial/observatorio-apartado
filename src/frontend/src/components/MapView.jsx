import { useEffect, useCallback, useMemo } from 'react'
import { Map } from 'react-map-gl/maplibre'
import DeckGL from '@deck.gl/react'
import { GeoJsonLayer, ScatterplotLayer } from '@deck.gl/layers'
import { HeatmapLayer } from '@deck.gl/aggregation-layers'
import { useStore } from '../store'

const MAP_STYLE = 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json'

const CATEGORY_COLORS = {
  'Restaurantes': [250, 140, 22],
  'Bancos': [0, 80, 179],
  'Farmacias': [82, 196, 26],
  'Hospitales': [245, 34, 45],
  'Colegios': [24, 144, 255],
  'Supermercados': [64, 169, 255],
  'Tiendas': [105, 192, 255],
  'Iglesias': [140, 140, 140],
  'Hoteles': [250, 140, 22],
  'Caféterías': [160, 120, 60],
  'Bares': [207, 19, 34],
  'Panaderías': [212, 107, 8],
  'Ferreterías': [89, 89, 89],
  'Talleres mecánicos': [89, 89, 89],
  'Salones de belleza': [194, 84, 148],
}

const DEFAULT_COLOR = [24, 144, 255]

function getCategoryColor(category) {
  return CATEGORY_COLORS[category] || DEFAULT_COLOR
}

function getPopulationColor(totalPersonas) {
  const maxPop = 500
  const t = Math.min(totalPersonas / maxPop, 1)
  return [
    Math.round(145 * (1 - t) + 0 * t),
    Math.round(213 * (1 - t) + 80 * t),
    Math.round(255 * (1 - t) + 179 * t),
  ]
}

export default function MapView() {
  const viewState = useStore((s) => s.viewState)
  const setViewState = useStore((s) => s.setViewState)
  const activeLayers = useStore((s) => s.activeLayers)
  const layerData = useStore((s) => s.layerData)
  const fetchLayerGeoJSON = useStore((s) => s.fetchLayerGeoJSON)
  const fetchManzanas = useStore((s) => s.fetchManzanas)
  const fetchPlaces = useStore((s) => s.fetchPlaces)
  const fetchPlacesHeatmap = useStore((s) => s.fetchPlacesHeatmap)

  useEffect(() => {
    fetchLayerGeoJSON('limite_municipal')
    fetchLayerGeoJSON('osm_edificaciones')
    fetchLayerGeoJSON('osm_vias')
    fetchManzanas()
    fetchPlaces()
    fetchPlacesHeatmap()
  }, [fetchLayerGeoJSON, fetchManzanas, fetchPlaces, fetchPlacesHeatmap])

  const onViewStateChange = useCallback(
    ({ viewState: vs }) => setViewState(vs),
    [setViewState],
  )

  const layers = useMemo(() => {
    const result = []

    if (activeLayers.includes('limite_municipal') && layerData.limite_municipal) {
      result.push(
        new GeoJsonLayer({
          id: 'limite_municipal',
          data: layerData.limite_municipal,
          filled: false,
          stroked: true,
          getLineColor: [0, 80, 179],
          getLineWidth: 2.5,
          lineWidthUnits: 'pixels',
        }),
      )
    }

    if (activeLayers.includes('osm_edificaciones') && layerData.osm_edificaciones) {
      result.push(
        new GeoJsonLayer({
          id: 'osm_edificaciones',
          data: layerData.osm_edificaciones,
          filled: true,
          stroked: false,
          getFillColor: [94, 102, 135],
          opacity: 0.3,
        }),
      )
    }

    if (activeLayers.includes('osm_vias') && layerData.osm_vias) {
      result.push(
        new GeoJsonLayer({
          id: 'osm_vias',
          data: layerData.osm_vias,
          filled: false,
          stroked: true,
          getLineColor: [0, 80, 179],
          opacity: 0.4,
          getLineWidth: 1,
          lineWidthUnits: 'pixels',
        }),
      )
    }

    if (activeLayers.includes('manzanas_censales') && layerData.manzanas) {
      result.push(
        new GeoJsonLayer({
          id: 'manzanas_censales',
          data: layerData.manzanas,
          filled: true,
          stroked: false,
          extruded: true,
          wireframe: false,
          opacity: 0.7,
          getElevation: (f) => {
            const pop = parseInt(f.properties.total_personas, 10) || 0
            return pop * 3
          },
          getFillColor: (f) => {
            const pop = parseInt(f.properties.total_personas, 10) || 0
            return getPopulationColor(pop)
          },
          material: {
            ambient: 0.4,
            diffuse: 0.6,
            shininess: 32,
          },
        }),
      )
    }

    if (activeLayers.includes('google_places') && layerData.places) {
      const features = layerData.places.features || []
      result.push(
        new ScatterplotLayer({
          id: 'google_places',
          data: features,
          getPosition: (f) => f.geometry.coordinates,
          getRadius: 40,
          radiusUnits: 'meters',
          getFillColor: (f) => getCategoryColor(f.properties.category),
          pickable: true,
        }),
      )
    }

    if (activeLayers.includes('places_heatmap') && layerData.placesHeatmap) {
      const heatData = layerData.placesHeatmap
      result.push(
        new HeatmapLayer({
          id: 'places_heatmap',
          data: heatData,
          getPosition: (d) => [d.lon, d.lat],
          getWeight: (d) => d.weight || 1,
          radiusPixels: 60,
          colorRange: [
            [198, 219, 239, 25],
            [158, 202, 225, 100],
            [107, 174, 214, 180],
            [66, 146, 198, 220],
            [33, 113, 181, 240],
            [8, 69, 148, 255],
          ],
          intensity: 1,
          threshold: 0.05,
        }),
      )
    }

    return result
  }, [activeLayers, layerData])

  const getTooltip = useCallback(({ object }) => {
    if (!object) return null
    const props = object.properties || object
    if (!props.name && !props.category) return null
    return {
      html: `
        <div style="
          background: #ffffff;
          border: 1px solid #DDE1E8;
          border-radius: 6px;
          padding: 8px 12px;
          font-family: 'Inter', sans-serif;
          font-size: 13px;
          color: #1A1F36;
          max-width: 260px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        ">
          ${props.name ? `<div style="font-weight: 600; color: #0050B3; margin-bottom: 4px;">${props.name}</div>` : ''}
          ${props.category ? `<div style="margin-bottom: 2px;"><span style="color: #5E6687;">Categoría:</span> ${props.category}</div>` : ''}
          ${props.rating != null ? `<div><span style="color: #5E6687;">Rating:</span> ${props.rating}</div>` : ''}
        </div>
      `,
      style: {
        backgroundColor: 'transparent',
        border: 'none',
        padding: 0,
      },
    }
  }, [])

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      <DeckGL
        viewState={viewState}
        onViewStateChange={onViewStateChange}
        controller={true}
        layers={layers}
        getTooltip={getTooltip}
      >
        <Map
          mapStyle={MAP_STYLE}
          reuseMaps
        />
      </DeckGL>
    </div>
  )
}
