import { useState, useEffect } from 'react'
import { useStore } from '../store'
import {
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer,
} from 'recharts'

const FALLBACK_OPTIONS = [
  { id: 'homicidios_anual', name: 'Homicidios/ano' },
  { id: 'hurtos_anual', name: 'Hurtos/ano' },
]

function getCorrelationLabel(r) {
  if (r == null || isNaN(r)) return ''
  const absR = Math.abs(r)
  if (absR < 0.3) return 'Correlacion debil'
  if (absR <= 0.7) return 'Correlacion moderada'
  return 'Correlacion fuerte'
}

export default function CrossvarScatter() {
  const { crossvarData, fetchCrossvar, crossvarVariables, fetchCrossvarVariables, errors } = useStore()
  const [varX, setVarX] = useState('homicidios_anual')
  const [varY, setVarY] = useState('hurtos_anual')

  useEffect(() => { fetchCrossvarVariables() }, [])
  useEffect(() => { fetchCrossvar(varX, varY) }, [varX, varY])

  const variables = crossvarVariables?.length ? crossvarVariables : FALLBACK_OPTIONS

  const selectStyle = {
    background: 'var(--bg-card)',
    color: 'var(--text-primary)',
    border: '1px solid var(--border)',
    borderRadius: 6,
    padding: '4px 8px',
    fontSize: 12,
    outline: 'none',
    fontFamily: 'inherit',
  }

  return (
    <div>
      <h3 className="section-title">Cruce de Variables</h3>
      <div style={{ display: 'flex', gap: 8, marginBottom: 12, flexWrap: 'wrap' }}>
        <div>
          <label style={{ fontSize: 10, color: 'var(--text-secondary)', display: 'block', marginBottom: 2 }}>EJE X</label>
          <select value={varX} onChange={(e) => setVarX(e.target.value)} style={selectStyle}>
            {variables.map((v) => <option key={v.id} value={v.id}>{v.name}</option>)}
          </select>
        </div>
        <div>
          <label style={{ fontSize: 10, color: 'var(--text-secondary)', display: 'block', marginBottom: 2 }}>EJE Y</label>
          <select value={varY} onChange={(e) => setVarY(e.target.value)} style={selectStyle}>
            {variables.map((v) => <option key={v.id} value={v.id}>{v.name}</option>)}
          </select>
        </div>
      </div>

      {crossvarData?.correlation !== undefined && (
        <div style={{ background: 'var(--bg-card)', borderRadius: 8, padding: '8px 12px', marginBottom: 10, border: '1px solid var(--border)', fontSize: 12 }}>
          <div>
            <span style={{ color: 'var(--text-secondary)' }}>r = </span>
            <span style={{ color: 'var(--accent-primary)', fontWeight: 'bold' }}>{crossvarData.correlation?.toFixed(3) || 'N/A'}</span>
            <span style={{ color: 'var(--text-secondary)', marginLeft: 12 }}>R² = </span>
            <span style={{ color: 'var(--semantic-positive)', fontWeight: 'bold' }}>{crossvarData.regression?.r_squared?.toFixed(3) || 'N/A'}</span>
            <span style={{ color: 'var(--text-secondary)', marginLeft: 12 }}>n = </span>
            <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{crossvarData.n}</span>
          </div>
          {crossvarData.correlation != null && (
            <div style={{ color: 'var(--text-muted)', fontSize: 11, marginTop: 4, fontStyle: 'italic' }}>
              {getCorrelationLabel(crossvarData.correlation)}
            </div>
          )}
        </div>
      )}

      {crossvarData?.points ? (
        <ResponsiveContainer width="100%" height={220}>
          <ScatterChart margin={{ left: 0, right: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border-light)" />
            <XAxis dataKey="x" type="number" name={crossvarData.var_x?.name} tick={{ fill: 'var(--text-secondary)', fontSize: 10 }}
              label={{ value: crossvarData.var_x?.name, position: 'bottom', fill: 'var(--text-secondary)', fontSize: 10 }} />
            <YAxis dataKey="y" type="number" name={crossvarData.var_y?.name} tick={{ fill: 'var(--text-secondary)', fontSize: 10 }} />
            <Tooltip
              content={({ payload }) => {
                if (!payload?.[0]) return null
                const d = payload[0].payload
                return (
                  <div style={{ background: 'var(--bg-card)', border: '1px solid var(--accent-primary)', borderRadius: 6, padding: 8, fontSize: 11, boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
                    <div style={{ color: 'var(--accent-primary)', fontWeight: 'bold' }}>{d.label}</div>
                    <div style={{ color: 'var(--text-secondary)' }}>X: {d.x} | Y: {d.y}</div>
                  </div>
                )
              }}
            />
            <Scatter data={crossvarData.points} fill="var(--accent-primary)" fillOpacity={0.75} r={5} />
          </ScatterChart>
        </ResponsiveContainer>
      ) : errors?.cruces ? (
        <div style={{ color: 'var(--semantic-negative)', padding: 16, fontSize: 12 }}>Error: {errors.cruces}</div>
      ) : (
        <div style={{ color: 'var(--text-muted)', padding: 16 }}>Cargando...</div>
      )}
      <div className="data-source">Fuentes: Policia Nacional, DANE, ICFES</div>
    </div>
  )
}
