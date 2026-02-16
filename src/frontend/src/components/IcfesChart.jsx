import { useEffect } from 'react'
import { useStore } from '../store'
import { SkeletonTab } from './Skeleton'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer,
} from 'recharts'

export default function IcfesChart() {
  const { icfesData, fetchIcfes } = useStore()

  useEffect(() => { fetchIcfes() }, [])

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
          <CartesianGrid strokeDasharray="3 3" stroke="#EBEEF3" />
          <XAxis dataKey="periodo" tick={{ fill: '#5E6687', fontSize: 9 }} angle={-45} textAnchor="end" height={50} />
          <YAxis tick={{ fill: '#5E6687', fontSize: 10 }} domain={[0, 300]} />
          <Tooltip
            contentStyle={{ background: '#FFFFFF', border: '1px solid #DDE1E8', borderRadius: 6, fontSize: 12 }}
            labelStyle={{ color: '#1A1F36', fontWeight: 600 }}
          />
          <Bar dataKey="global" fill="#0050B3" opacity={0.9} radius={[4, 4, 0, 0]} name="Global" />
          <Bar dataKey="matematicas" fill="#40A9FF" opacity={0.8} radius={[4, 4, 0, 0]} name="Matematicas" />
        </BarChart>
      </ResponsiveContainer>
      <div className="data-source">Fuente: ICFES Saber 11 — datos.gov.co</div>
    </div>
  )
}
