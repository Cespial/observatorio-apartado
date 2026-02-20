import DashboardCard from './DashboardCard'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell,
} from 'recharts'

const COLORS = ['#0050B3', '#1890FF', '#40A9FF', '#69C0FF', '#52C41A', '#FA8C16', '#F5222D', '#722ED1']

const tooltipStyle = {
  background: 'var(--bg-card)', border: '1px solid var(--border)',
  borderRadius: 6, fontSize: 12,
}

export default function EnrichmentCharts({ enrichmentData }) {
  if (!enrichmentData) return null
  const { experiencia, contratos, educacion, modalidad } = enrichmentData

  return (
    <DashboardCard span={2} title="Perfil de Ofertas" subtitle="Experiencia, contrato, educacion, modalidad">
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        {/* Experiencia requerida */}
        {experiencia?.length > 0 && (
          <div>
            <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
              Experiencia requerida
            </div>
            <ResponsiveContainer width="100%" height={140}>
              <BarChart data={experiencia} layout="vertical" margin={{ left: 0, right: 10 }}>
                <XAxis type="number" tick={{ fill: 'var(--text-secondary)', fontSize: 9 }} />
                <YAxis dataKey="nivel" type="category" width={90} tick={{ fill: 'var(--text-secondary)', fontSize: 9 }} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar dataKey="total" radius={[0, 4, 4, 0]}>
                  {experiencia.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} fillOpacity={0.85} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Tipo de contrato */}
        {contratos?.length > 0 && (
          <div>
            <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
              Tipo de contrato
            </div>
            <ResponsiveContainer width="100%" height={140}>
              <PieChart>
                <Pie
                  data={contratos} dataKey="total" nameKey="tipo"
                  cx="50%" cy="50%" outerRadius={55} innerRadius={25}
                  label={({ tipo, total }) => `${tipo}: ${total}`}
                  labelLine={{ stroke: 'var(--text-muted)', strokeWidth: 1 }}
                >
                  {contratos.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} fillOpacity={0.85} />
                  ))}
                </Pie>
                <Tooltip contentStyle={tooltipStyle} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Nivel educativo */}
        {educacion?.length > 0 && (
          <div>
            <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
              Nivel educativo
            </div>
            <ResponsiveContainer width="100%" height={140}>
              <BarChart data={educacion} layout="vertical" margin={{ left: 0, right: 10 }}>
                <XAxis type="number" tick={{ fill: 'var(--text-secondary)', fontSize: 9 }} />
                <YAxis dataKey="nivel" type="category" width={90} tick={{ fill: 'var(--text-secondary)', fontSize: 9 }} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar dataKey="total" radius={[0, 4, 4, 0]}>
                  {educacion.map((_, i) => (
                    <Cell key={i} fill={COLORS[(i + 3) % COLORS.length]} fillOpacity={0.85} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Modalidad */}
        {modalidad?.length > 0 && (
          <div>
            <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
              Modalidad de trabajo
            </div>
            <ResponsiveContainer width="100%" height={140}>
              <PieChart>
                <Pie
                  data={modalidad} dataKey="total" nameKey="modalidad"
                  cx="50%" cy="50%" outerRadius={55} innerRadius={25}
                  label={({ modalidad: m, total }) => `${m}: ${total}`}
                  labelLine={{ stroke: 'var(--text-muted)', strokeWidth: 1 }}
                >
                  {modalidad.map((_, i) => (
                    <Cell key={i} fill={COLORS[(i + 5) % COLORS.length]} fillOpacity={0.85} />
                  ))}
                </Pie>
                <Tooltip contentStyle={tooltipStyle} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </DashboardCard>
  )
}
