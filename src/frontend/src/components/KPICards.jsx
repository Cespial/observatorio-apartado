const CARDS = [
  { key: 'poblacion_total', label: 'Poblacion total', source: 'DANE', year: '2019' },
  { key: 'manzanas_censales', label: 'Manzanas censales', source: 'MGN-DANE', year: '2023' },
  { key: 'edificaciones_osm', label: 'Edificaciones', source: 'OSM', year: '2025' },
  { key: 'establecimientos_comerciales', label: 'Negocios mapeados', source: 'Google Places', year: '2025' },
  { key: 'establecimientos_educativos', label: 'Establec. educativos', source: 'MEN', year: '2024' },
  { key: 'ips_salud', label: 'IPS habilitadas', source: 'REPS', year: '2024' },
  { key: 'total_homicidios', label: 'Homicidios', source: 'Policia Nal.', year: '2015-2024', negative: true },
  { key: 'total_victimas_conflicto', label: 'Victimas conflicto', source: 'Unidad Victimas', year: '1985-2024', negative: true },
]

function fmt(val) {
  if (val == null) return '---'
  if (typeof val === 'number') return val.toLocaleString('es-CO')
  return String(val)
}

export default function KPICards({ summary }) {
  if (!summary) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '10px 24px', fontSize: 13, color: 'var(--text-muted)' }}>
        Cargando indicadores...
      </div>
    )
  }

  return (
    <div className="kpi-strip" style={{ display: 'flex', gap: 12, padding: '10px 24px', overflowX: 'auto', flexShrink: 0, background: 'var(--bg-primary)', borderBottom: '1px solid var(--border)' }}>
      {CARDS.map((card) => (
        <div
          key={card.key}
          className="card"
          style={{ padding: '10px 14px', minWidth: 140, flexShrink: 0 }}
        >
          <div
            style={{
              fontSize: 22,
              fontWeight: 700,
              color: card.negative ? 'var(--semantic-negative)' : 'var(--text-primary)',
              lineHeight: 1.2,
              fontFeatureSettings: '"tnum"',
            }}
          >
            {fmt(summary[card.key])}
          </div>
          <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 2 }}>
            {card.label}
          </div>
          <div className="font-mono" style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 3 }}>
            {card.source} &middot; {card.year}
          </div>
        </div>
      ))}
    </div>
  )
}
