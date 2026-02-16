import { useStore } from '../store';

const LAYERS = [
  { id: 'limite_municipal', label: 'Límite Municipal', color: '#0050B3' },
  { id: 'manzanas_censales', label: 'Manzanas 3D', color: '#1890FF' },
  { id: 'osm_edificaciones', label: 'Edificaciones', color: '#5E6687' },
  { id: 'osm_vias', label: 'Red Vial', color: '#40A9FF' },
  { id: 'google_places', label: 'Negocios', color: '#FA8C16' },
  { id: 'places_heatmap', label: 'Heatmap Negocios', color: '#0050B3' },
];

export default function LayerPanel() {
  const activeLayers = useStore((s) => s.activeLayers);
  const toggleLayer = useStore((s) => s.toggleLayer);

  return (
    <div
      style={{
        position: 'absolute',
        top: 12,
        left: 12,
        zIndex: 10,
        background: '#FFFFFF',
        borderRadius: 8,
        border: '1px solid #DDE1E8',
        padding: 12,
        minWidth: 190,
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      }}
    >
      <div
        style={{
          fontSize: 10,
          fontWeight: 700,
          letterSpacing: '0.12em',
          color: '#1A1F36',
          marginBottom: 8,
          textTransform: 'uppercase',
        }}
      >
        Capas
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {LAYERS.map((layer) => {
          const active = activeLayers.includes(layer.id);
          return (
            <div
              key={layer.id}
              onClick={() => toggleLayer(layer.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                cursor: 'pointer',
                opacity: active ? 1 : 0.45,
                transition: 'opacity 0.2s ease',
              }}
            >
              {/* Color dot */}
              <span
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  background: layer.color,
                  flexShrink: 0,
                  boxShadow: active ? `0 0 6px ${layer.color}` : 'none',
                }}
              />

              {/* Label */}
              <span style={{ fontSize: 12, color: active ? '#1A1F36' : '#5E6687', flex: 1 }}>
                {layer.label}
              </span>

              {/* Toggle indicator */}
              <span
                style={{
                  width: 28,
                  height: 14,
                  borderRadius: 7,
                  background: active ? 'rgba(0,80,179,0.2)' : '#DDE1E8',
                  position: 'relative',
                  transition: 'background 0.2s ease',
                  flexShrink: 0,
                }}
              >
                <span
                  style={{
                    position: 'absolute',
                    top: 2,
                    left: active ? 14 : 2,
                    width: 10,
                    height: 10,
                    borderRadius: '50%',
                    background: active ? '#0050B3' : '#DDE1E8',
                    transition: 'left 0.2s ease, background 0.2s ease',
                  }}
                />
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
