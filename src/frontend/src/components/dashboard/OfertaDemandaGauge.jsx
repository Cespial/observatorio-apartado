import DashboardCard from './DashboardCard'

export default function OfertaDemandaGauge({ data }) {
  if (!data?.length) return null

  const maxRate = Math.max(...data.map(d => d.vacantes_por_1000_hab || 0), 1)

  return (
    <DashboardCard title="Oferta vs Demanda" subtitle="Vacantes por 1,000 habitantes">
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {data.slice(0, 8).map((item, i) => {
          const pct = maxRate > 0 ? (item.vacantes_por_1000_hab / maxRate) * 100 : 0
          return (
            <div key={i}>
              <div style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                fontSize: 11, color: 'var(--text-secondary)', marginBottom: 2,
              }}>
                <span>{item.municipio}</span>
                <span style={{ fontWeight: 600, color: 'var(--accent-primary)' }}>
                  {item.vacantes_por_1000_hab?.toFixed(1)}
                </span>
              </div>
              <div style={{
                display: 'flex', gap: 2, height: 14, borderRadius: 3, overflow: 'hidden',
                background: 'var(--bg-tertiary)',
              }}>
                <div
                  style={{
                    width: `${pct}%`,
                    background: `linear-gradient(90deg, #0050B3, #1890FF)`,
                    borderRadius: 3,
                    transition: 'width 0.6s ease',
                    minWidth: pct > 0 ? 4 : 0,
                  }}
                  title={`${item.vacantes} vacantes / ${item.poblacion?.toLocaleString('es-CO')} hab.`}
                />
              </div>
              <div style={{ fontSize: 9, color: 'var(--text-muted)', marginTop: 1 }}>
                {item.vacantes} vacantes | {item.poblacion?.toLocaleString('es-CO')} hab.
              </div>
            </div>
          )
        })}
      </div>
    </DashboardCard>
  )
}
