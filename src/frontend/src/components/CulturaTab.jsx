import { useEffect } from 'react'
import { useStore } from '../store'
import { SkeletonTab, ErrorBanner, ExportCSVButton } from './Skeleton'

const TYPE_COLORS = {
  'Biblioteca Pública': 'var(--accent-primary)',
  'Espacio para las Artes Escénicas': 'var(--semantic-warning)',
  'Centro Musical Batuta': 'var(--semantic-positive)',
  'Archivo Histórico': 'var(--text-muted)',
}

export default function CulturaTab() {
  const { culturaData, fetchCultura, errors } = useStore()

  useEffect(() => { fetchCultura() }, [])

  if (errors.cultura) return <ErrorBanner message={errors.cultura} />
  if (!culturaData) return <SkeletonTab />

  const { espacios, turismo } = culturaData

  const byType = {}
  espacios?.forEach((e) => {
    byType[e.tipo_lugar] = (byType[e.tipo_lugar] || 0) + 1
  })

  const turCats = turismo?.por_categoria ? Object.entries(turismo.por_categoria) : []

  return (
    <div className="fade-in">
      <h3 className="section-title">Cultura y Turismo</h3>

      {/* Espacios culturales summary */}
      {espacios?.length > 0 && (
        <>
          <h4 className="section-title" style={{ fontSize: 11 }}>
            Espacios Culturales ({espacios.length})
          </h4>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 12 }}>
            {Object.entries(byType).map(([tipo, count]) => (
              <div key={tipo} style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border)',
                borderRadius: 6,
                padding: '6px 10px',
                flex: '1 1 45%',
                minWidth: 140,
              }}>
                <div style={{ fontSize: 10, color: 'var(--text-secondary)' }}>{tipo}</div>
                <div style={{ fontSize: 18, fontWeight: 700, color: TYPE_COLORS[tipo] || 'var(--accent-primary)' }}>{count}</div>
              </div>
            ))}
          </div>

          {/* Espacios list */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginBottom: 12 }}>
            {espacios.map((e, i) => (
              <div key={i} style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border)',
                borderRadius: 6,
                padding: '8px 10px',
              }}>
                <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 2 }}>
                  {e.nombre}
                </div>
                <div style={{ fontSize: 10, color: 'var(--text-secondary)', marginBottom: 2 }}>
                  {e.tipo_lugar}
                </div>
                {e.descripcion && (
                  <div style={{ fontSize: 10, color: 'var(--text-muted)', lineHeight: 1.4 }}>
                    {e.descripcion.length > 120 ? e.descripcion.slice(0, 120) + '...' : e.descripcion}
                  </div>
                )}
                {e.direccion && (
                  <div style={{ fontSize: 9, color: 'var(--text-muted)', marginTop: 2 }}>
                    {e.direccion}
                  </div>
                )}
              </div>
            ))}
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div className="data-source">Fuente: MinCultura — datos.gov.co</div>
            <ExportCSVButton rows={espacios} filename="espacios_culturales.csv" />
          </div>
        </>
      )}

      {/* Turismo RNT */}
      {turCats.length > 0 && (
        <>
          <h4 className="section-title" style={{ fontSize: 11, marginTop: 16 }}>
            Registro Nacional de Turismo ({turismo.total} estab.)
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {turCats.map(([cat, data]) => (
              <div key={cat} style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border)',
                borderRadius: 6,
                padding: '8px 10px',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: 11, color: 'var(--text-secondary)' }}>
                    {cat.length > 35 ? cat.slice(0, 35) + '...' : cat}
                  </span>
                  <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--accent-primary)' }}>{data.count}</span>
                </div>
                {data.establecimientos.slice(0, 3).map((e, i) => (
                  <div key={i} style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2, paddingLeft: 8, borderLeft: '2px solid var(--border)' }}>
                    {e.nombre}
                    {e.habitaciones ? ` · ${e.habitaciones} hab.` : ''}
                    {e.empleados ? ` · ${e.empleados} emp.` : ''}
                  </div>
                ))}
                {data.count > 3 && (
                  <div style={{ fontSize: 9, color: 'var(--text-muted)', marginTop: 2, paddingLeft: 8 }}>
                    +{data.count - 3} mas...
                  </div>
                )}
              </div>
            ))}
          </div>
          <div className="data-source" style={{ marginTop: 6 }}>Fuente: MinCIT — RNT via datos.gov.co</div>
        </>
      )}
    </div>
  )
}
