import { useMemo } from 'react'
import DashboardCard from './DashboardCard'

function interpolateColor(val, max) {
  if (!val || max === 0) return '#EDF0F4'
  const t = Math.min(val / max, 1)
  // Interpolate from #EDF0F4 (light) to #0050B3 (dark blue)
  const r = Math.round(237 + (0 - 237) * t)
  const g = Math.round(240 + (80 - 240) * t)
  const b = Math.round(244 + (179 - 244) * t)
  return `rgb(${r},${g},${b})`
}

export default function SectorMunicipioHeatmap({ data }) {
  const { sectors, municipios, maxVal } = useMemo(() => {
    if (!data?.length) return { sectors: [], municipios: [], maxVal: 0 }

    // Get all unique municipio names (exclude 'sector' and 'total' keys)
    const muniSet = new Set()
    let mx = 0
    for (const row of data) {
      for (const key of Object.keys(row)) {
        if (key !== 'sector' && key !== 'total') {
          muniSet.add(key)
          if (row[key] > mx) mx = row[key]
        }
      }
    }

    return {
      sectors: data.slice(0, 10),
      municipios: Array.from(muniSet).sort(),
      maxVal: mx,
    }
  }, [data])

  if (!sectors.length || !municipios.length) return null

  const cols = municipios.length + 1 // +1 for sector label column

  return (
    <DashboardCard span={2} title="Sector x Municipio" subtitle="Ofertas por sector en cada municipio">
      <div style={{ overflowX: 'auto' }}>
        <div
          className="heatmap-grid"
          style={{ gridTemplateColumns: `140px repeat(${municipios.length}, 1fr)` }}
        >
          {/* Header row */}
          <div style={{ fontSize: 9, fontWeight: 600, color: 'var(--text-muted)', padding: '4px 6px' }} />
          {municipios.map(m => (
            <div key={m} style={{
              fontSize: 9, fontWeight: 600, color: 'var(--text-secondary)',
              textAlign: 'center', padding: '4px 2px',
              overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
            }}>
              {m.length > 10 ? m.slice(0, 10) + '..' : m}
            </div>
          ))}

          {/* Data rows */}
          {sectors.map(row => (
            <>
              <div key={`label-${row.sector}`} style={{
                fontSize: 10, fontWeight: 600, color: 'var(--text-secondary)',
                padding: '4px 6px', display: 'flex', alignItems: 'center',
                overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
              }}>
                {row.sector}
              </div>
              {municipios.map(m => {
                const val = row[m] || 0
                const bg = interpolateColor(val, maxVal)
                const textColor = val > maxVal * 0.5 ? '#fff' : 'var(--text-secondary)'
                return (
                  <div
                    key={`${row.sector}-${m}`}
                    className="heatmap-cell"
                    style={{ background: bg, color: textColor }}
                    title={`${val} ofertas de ${row.sector} en ${m}`}
                  >
                    {val > 0 ? val : ''}
                  </div>
                )
              })}
            </>
          ))}
        </div>
      </div>
    </DashboardCard>
  )
}
