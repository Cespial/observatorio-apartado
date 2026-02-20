import { useEffect } from 'react'
import { useStore } from '../store'
import { SkeletonTab, ErrorBanner, ExportCSVButton } from './Skeleton'

export default function CulturaTab() {
  const { culturaData, fetchCultura, errors } = useStore()

  useEffect(() => { fetchCultura() }, [])

  if (errors.cultura) return <ErrorBanner message={errors.cultura} />
  if (!culturaData) return <SkeletonTab />

  const { espacios, turismo } = culturaData

  // API returns {indicador, valor, anio, municipio} from TerriData
  const turCats = turismo?.por_categoria ? Object.entries(turismo.por_categoria) : []

  return (
    <div className="fade-in">
      <h3 className="section-title">Cultura y Turismo</h3>

      {/* Cultural indicators from TerriData */}
      {espacios?.length > 0 && (
        <>
          <h4 className="section-title" style={{ fontSize: 11 }}>
            Indicadores Culturales
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4, marginBottom: 12 }}>
            {espacios.map((e, i) => (
              <div key={i} style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '6px 10px',
                background: 'var(--bg-card)',
                border: '1px solid var(--border)',
                borderRadius: 6,
              }}>
                <span style={{ fontSize: 11, color: 'var(--text-secondary)', flex: 1 }}>
                  {e.indicador?.length > 40 ? e.indicador.slice(0, 40) + '...' : e.indicador}
                </span>
                <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--accent-primary)', marginLeft: 8 }}>
                  {typeof e.valor === 'number' ? e.valor.toLocaleString('es-CO') : e.valor}
                  {e.anio && <span style={{ color: 'var(--text-muted)', fontWeight: 400, fontSize: 9, marginLeft: 4 }}>({e.anio})</span>}
                </span>
              </div>
            ))}
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div className="data-source">Fuente: DNP — TerriData</div>
            <ExportCSVButton rows={espacios} filename="cultura_indicadores.csv" />
          </div>
        </>
      )}

      {/* Turismo from Google Places */}
      {turCats.length > 0 && (
        <>
          <h4 className="section-title" style={{ fontSize: 11, marginTop: 16 }}>
            Establecimientos Turisticos ({turismo.total || 0} total)
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            {turCats.map(([cat, data]) => (
              <div key={cat} style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '6px 10px',
                background: 'var(--bg-card)',
                border: '1px solid var(--border)',
                borderRadius: 6,
              }}>
                <span style={{ fontSize: 11, color: 'var(--text-secondary)' }}>
                  {cat.length > 35 ? cat.slice(0, 35) + '...' : cat}
                </span>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--accent-primary)' }}>{data.total}</span>
                  {data.avg_rating != null && (
                    <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>
                      {Number(data.avg_rating).toFixed(1)} &#9733;
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
          <div className="data-source" style={{ marginTop: 6 }}>Fuente: Google Places</div>
        </>
      )}
    </div>
  )
}
