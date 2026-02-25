import { useMemo } from 'react'

export default function InsightsBar({ empleoKpis, empleoData, enrichmentData }) {
  const insights = useMemo(() => {
    const items = []
    const kpis = empleoKpis
    const stats = empleoData?.stats
    const skills = empleoData?.skills
    const sectores = empleoData?.sectores

    // Top sector
    if (sectores?.length > 0) {
      const top = sectores[0]
      const total = kpis?.total_ofertas || stats?.total_ofertas || 0
      const pct = total > 0 ? Math.round((top.ofertas / total) * 100) : 0
      items.push({ icon: '\uD83C\uDFE2', text: `El sector con mas demanda es ${top.sector} con ${top.ofertas} ofertas (${pct}%)`, type: 'sector' })
    }

    // Top skill
    if (skills?.length > 0) {
      items.push({ icon: '\u26A1', text: `${skills[0].skill} es la habilidad mas solicitada, aparece en ${skills[0].demanda} ofertas`, type: 'skill' })
    }

    // Salary coverage
    if (stats) {
      const total = kpis?.total_ofertas || stats.total_ofertas || 0
      const conSalario = stats.con_salario || 0
      if (total > 0) {
        const sinPct = Math.round(((total - conSalario) / total) * 100)
        if (sinPct > 30) {
          items.push({ icon: '\uD83D\uDCB0', text: `El ${sinPct}% de las ofertas no publican salario`, type: 'salary' })
        }
      }
    }

    // Concentration
    if (stats?.por_municipio?.length > 0) {
      const top = stats.por_municipio[0]
      const total = kpis?.total_ofertas || stats.total_ofertas || 0
      const pct = total > 0 ? Math.round((top.total / total) * 100) : 0
      if (pct > 30) {
        items.push({ icon: '\uD83D\uDCCD', text: `${top.municipio} concentra el ${pct}% de las vacantes de la region`, type: 'geo' })
      }
    }

    // Experiencia
    if (enrichmentData?.experiencia?.length > 0) {
      const conExp = enrichmentData.experiencia
        .filter(e => e.nivel !== 'Sin experiencia')
        .reduce((s, e) => s + e.total, 0)
      const totalExp = enrichmentData.experiencia.reduce((s, e) => s + e.total, 0)
      if (totalExp > 0) {
        const pct = Math.round((conExp / totalExp) * 100)
        if (pct > 40) {
          items.push({ icon: '\uD83C\uDFAF', text: `El ${pct}% de ofertas requieren experiencia de 1+ anos`, type: 'experience' })
        }
      }
    }

    // Modalidad
    if (enrichmentData?.modalidad?.length > 0) {
      const presencial = enrichmentData.modalidad.find(m => m.modalidad === 'Presencial')
      const total = enrichmentData.modalidad.reduce((s, m) => s + m.total, 0)
      if (presencial && total > 0) {
        const pct = Math.round((presencial.total / total) * 100)
        if (pct > 50) {
          items.push({ icon: '\uD83C\uDFE0', text: `El ${pct}% de las ofertas son presenciales`, type: 'modality' })
        }
      }
    }

    return items.slice(0, 5)
  }, [empleoKpis, empleoData, enrichmentData])

  if (insights.length === 0) return null

  return (
    <div className="dashboard-card card" style={{ gridColumn: 'span 3', padding: '12px 18px' }}>
      <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: 8 }}>
        Insights automaticos
      </div>
      <div className="insights-bar">
        {insights.map((item, i) => (
          <div
            key={i}
            className="insight-chip"
            style={{ animationDelay: `${i * 100}ms` }}
          >
            <span style={{ marginRight: 6 }}>{item.icon}</span>
            {item.text.split(/(\d+%?)/g).map((part, j) =>
              /^\d+%?$/.test(part)
                ? <strong key={j} style={{ color: 'var(--accent-primary)' }}>{part}</strong>
                : part
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
