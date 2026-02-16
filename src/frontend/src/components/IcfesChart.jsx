import { useEffect } from 'react'
import { useStore } from '../store'
import { SkeletonTab, ErrorBanner } from './Skeleton'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer,
} from 'recharts'

export default function IcfesChart() {
  const { icfesData, fetchIcfes, errors } = useStore()

  useEffect(() => { fetchIcfes() }, [])

  if (errors.educacion) return <ErrorBanner message={errors.educacion} />
  if (!icfesData) return <SkeletonTab />

  const data = icfesData
    .filter((d) => d.prom_global !== null)
    .map((d) => ({
      periodo: d.periodo,
      global: Math.round(d.prom_global),
      matematicas: Math.round(d.prom_matematicas || 0),
      estudiantes: d.estudiantes,
    }))

  return (
    <div className="fade-in">
      <h3 className="section-title">ICFES Saber 11 — Promedio por Periodo</h3>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border-light)" />
          <XAxis dataKey="periodo" tick={{ fill: 'var(--text-secondary)', fontSize: 9 }} angle={-45} textAnchor="end" height={50} />
          <YAxis tick={{ fill: 'var(--text-secondary)', fontSize: 10 }} domain={[0, 300]} />
          <Tooltip
            contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 6, fontSize: 12 }}
            labelStyle={{ color: 'var(--text-primary)', fontWeight: 600 }}
          />
          <Bar dataKey="global" fill="#0050B3" opacity={0.9} radius={[4, 4, 0, 0]} name="Global" />
          <Bar dataKey="matematicas" fill="#40A9FF" opacity={0.8} radius={[4, 4, 0, 0]} name="Matematicas" />
        </BarChart>
      </ResponsiveContainer>
      <div className="data-source">Fuente: ICFES Saber 11 — datos.gov.co</div>
    </div>
  )
}
