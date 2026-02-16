import { useEffect } from 'react'
import { useStore } from '../store'
import { SkeletonTab } from './Skeleton'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend,
} from 'recharts'

const COLORS = {
  'Homicidios': '#F5222D',
  'Hurtos': '#0050B3',
  'Delitos Sexuales': '#FA8C16',
  'Violencia Intrafamiliar': '#1890FF',
}

export default function SecurityChart() {
  const { securityMatrix, fetchSecurityMatrix } = useStore()

  useEffect(() => { fetchSecurityMatrix() }, [])

  if (!securityMatrix) return <SkeletonTab />

  const years = [...new Set(securityMatrix.map((d) => d.anio))].sort()
  const pivoted = years.map((y) => {
    const row = { anio: y }
    securityMatrix.filter((d) => d.anio === y).forEach((d) => {
      row[d.tipo] = d.total
    })
    return row
  })

  return (
    <div className="fade-in">
      <h3 className="section-title">Delitos por Ano</h3>
      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={pivoted}>
          <CartesianGrid strokeDasharray="3 3" stroke="#EBEEF3" />
          <XAxis dataKey="anio" tick={{ fill: '#5E6687', fontSize: 10 }} />
          <YAxis tick={{ fill: '#5E6687', fontSize: 10 }} />
          <Tooltip
            contentStyle={{ background: '#FFFFFF', border: '1px solid #DDE1E8', borderRadius: 6, fontSize: 12 }}
            labelStyle={{ color: '#1A1F36', fontWeight: 600 }}
          />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          {Object.entries(COLORS).map(([key, color]) => (
            <Area
              key={key}
              type="monotone"
              dataKey={key}
              stroke={color}
              fill={color}
              fillOpacity={0.12}
              strokeWidth={2}
            />
          ))}
        </AreaChart>
      </ResponsiveContainer>
      <div className="data-source">Fuente: Policia Nacional — datos.gov.co</div>
    </div>
  )
}
