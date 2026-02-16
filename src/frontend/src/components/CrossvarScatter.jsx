import { useState, useEffect } from 'react'
import { useStore } from '../store'
import {
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer,
} from 'recharts'

const VARIABLE_OPTIONS = [
  { id: 'homicidios_anual', label: 'Homicidios/ano' },
  { id: 'hurtos_anual', label: 'Hurtos/ano' },
  { id: 'vif_anual', label: 'VIF/ano' },
  { id: 'delitos_sexuales_anual', label: 'Del. Sexuales/ano' },
  { id: 'icfes_global', label: 'ICFES Global' },
  { id: 'icfes_matematicas', label: 'ICFES Matematicas' },
  { id: 'matricula', label: 'Matricula' },
  { id: 'places_categoria', label: 'Negocios/cat.' },
  { id: 'places_rating', label: 'Rating negocios' },
]

function getCorrelationLabel(r) {
  if (r == null || isNaN(r)) return ''
  const absR = Math.abs(r)
  if (absR < 0.3) return 'Correlacion debil'
  if (absR <= 0.7) return 'Correlacion moderada'
  return 'Correlacion fuerte'
}

export default function CrossvarScatter() {
  const { crossvarData, fetchCrossvar } = useStore()
  const [varX, setVarX] = useState('homicidios_anual')
  const [varY, setVarY] = useState('hurtos_anual')

  useEffect(() => { fetchCrossvar(varX, varY) }, [varX, varY])

  const selectStyle = {
    background: '#FFFFFF',
    color: '#1A1F36',
    border: '1px solid #DDE1E8',
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
          <label style={{ fontSize: 10, color: '#5E6687', display: 'block', marginBottom: 2 }}>EJE X</label>
          <select value={varX} onChange={(e) => setVarX(e.target.value)} style={selectStyle}>
            {VARIABLE_OPTIONS.map((v) => <option key={v.id} value={v.id}>{v.label}</option>)}
          </select>
        </div>
        <div>
          <label style={{ fontSize: 10, color: '#5E6687', display: 'block', marginBottom: 2 }}>EJE Y</label>
          <select value={varY} onChange={(e) => setVarY(e.target.value)} style={selectStyle}>
            {VARIABLE_OPTIONS.map((v) => <option key={v.id} value={v.id}>{v.label}</option>)}
          </select>
        </div>
      </div>

      {crossvarData?.correlation !== undefined && (
        <div style={{ background: '#FFFFFF', borderRadius: 8, padding: '8px 12px', marginBottom: 10, border: '1px solid #DDE1E8', fontSize: 12 }}>
          <div>
            <span style={{ color: '#5E6687' }}>r = </span>
            <span style={{ color: '#0050B3', fontWeight: 'bold' }}>{crossvarData.correlation?.toFixed(3) || 'N/A'}</span>
            <span style={{ color: '#5E6687', marginLeft: 12 }}>R² = </span>
            <span style={{ color: '#52C41A', fontWeight: 'bold' }}>{crossvarData.regression?.r_squared?.toFixed(3) || 'N/A'}</span>
            <span style={{ color: '#5E6687', marginLeft: 12 }}>n = </span>
            <span style={{ color: '#1A1F36', fontWeight: 600 }}>{crossvarData.n}</span>
          </div>
          {crossvarData.correlation != null && (
            <div style={{ color: '#8E94A9', fontSize: 11, marginTop: 4, fontStyle: 'italic' }}>
              {getCorrelationLabel(crossvarData.correlation)}
            </div>
          )}
        </div>
      )}

      {crossvarData?.points ? (
        <ResponsiveContainer width="100%" height={220}>
          <ScatterChart margin={{ left: 0, right: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#EBEEF3" />
            <XAxis dataKey="x" type="number" name={crossvarData.var_x?.name} tick={{ fill: '#5E6687', fontSize: 10 }}
              label={{ value: crossvarData.var_x?.name, position: 'bottom', fill: '#5E6687', fontSize: 10 }} />
            <YAxis dataKey="y" type="number" name={crossvarData.var_y?.name} tick={{ fill: '#5E6687', fontSize: 10 }} />
            <Tooltip
              content={({ payload }) => {
                if (!payload?.[0]) return null
                const d = payload[0].payload
                return (
                  <div style={{ background: '#FFFFFF', border: '1px solid #0050B3', borderRadius: 6, padding: 8, fontSize: 11, boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
                    <div style={{ color: '#0050B3', fontWeight: 'bold' }}>{d.label}</div>
                    <div style={{ color: '#5E6687' }}>X: {d.x} | Y: {d.y}</div>
                  </div>
                )
              }}
            />
            <Scatter data={crossvarData.points} fill="#0050B3" fillOpacity={0.75} r={5} />
          </ScatterChart>
        </ResponsiveContainer>
      ) : (
        <div style={{ color: '#8E94A9', padding: 16 }}>Cargando...</div>
      )}
      <div className="data-source">Fuentes: Policia Nacional, DANE, ICFES</div>
    </div>
  )
}
