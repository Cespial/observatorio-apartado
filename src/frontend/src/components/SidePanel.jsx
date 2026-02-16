import { useRef, useCallback, lazy, Suspense } from 'react'
import { useStore } from '../store'
import { SkeletonTab } from './Skeleton'

const SecurityChart = lazy(() => import('./SecurityChart'))
const IcfesChart = lazy(() => import('./IcfesChart'))
const VictimasChart = lazy(() => import('./VictimasChart'))
const CrossvarScatter = lazy(() => import('./CrossvarScatter'))
const SaludTab = lazy(() => import('./SaludTab'))
const EconomiaTab = lazy(() => import('./EconomiaTab'))
const GobiernoTab = lazy(() => import('./GobiernoTab'))

const TABS = [
  { id: 'overview', label: 'General' },
  { id: 'seguridad', label: 'Seguridad' },
  { id: 'educacion', label: 'Educacion' },
  { id: 'salud', label: 'Salud' },
  { id: 'economia', label: 'Economia' },
  { id: 'gobierno', label: 'Gobierno' },
  { id: 'victimas', label: 'Victimas' },
  { id: 'cruces', label: 'Cruces' },
]

export default function SidePanel() {
  const activePanel = useStore((s) => s.activePanel)
  const setActivePanel = useStore((s) => s.setActivePanel)
  const summary = useStore((s) => s.summary)
  const contentRef = useRef(null)

  const handleExport = useCallback(async () => {
    if (!contentRef.current) return
    const html2canvas = (await import('html2canvas')).default
    const canvas = await html2canvas(contentRef.current, {
      backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--bg-secondary').trim(),
      scale: 2,
    })
    const link = document.createElement('a')
    link.download = `observatorio-${activePanel}-${new Date().toISOString().slice(0, 10)}.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
  }, [activePanel])

  return (
    <div
      className="side-panel"
      style={{
        width: 400,
        flexShrink: 0,
        background: 'var(--bg-secondary)',
        borderLeft: '1px solid var(--border)',
        display: 'flex',
        flexDirection: 'column',
        overflowY: 'auto',
        height: '100%',
      }}
    >
      <div style={{ flexShrink: 0, display: 'flex', alignItems: 'center', borderBottom: '1px solid var(--border)' }}>
        <div className="tab-bar" style={{ flex: 1, flexWrap: 'wrap', border: 'none' }}>
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActivePanel(tab.id)}
              className={activePanel === tab.id ? 'tab-item active' : 'tab-item'}
            >
              {tab.label}
            </button>
          ))}
        </div>
        <button
          onClick={handleExport}
          title="Exportar como imagen PNG"
          style={{
            background: 'var(--bg-tertiary)',
            border: '1px solid var(--border)',
            borderRadius: 6,
            width: 28,
            height: 28,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            fontSize: 13,
            color: 'var(--text-secondary)',
            marginRight: 8,
            flexShrink: 0,
          }}
        >
          &#8681;
        </button>
      </div>

      <div ref={contentRef} style={{ flex: 1, padding: 16 }}>
        {activePanel === 'overview' && <OverviewPanel summary={summary} />}
        <Suspense fallback={<SkeletonTab />}>
          {activePanel === 'seguridad' && <SecurityChart />}
          {activePanel === 'educacion' && <IcfesChart />}
          {activePanel === 'salud' && <SaludTab />}
          {activePanel === 'economia' && <EconomiaTab />}
          {activePanel === 'gobierno' && <GobiernoTab />}
          {activePanel === 'victimas' && <VictimasChart />}
          {activePanel === 'cruces' && <CrossvarScatter />}
        </Suspense>
      </div>
    </div>
  )
}

function OverviewPanel({ summary }) {
  if (!summary) return <div style={{ color: 'var(--text-muted)', padding: 16 }}>Cargando...</div>

  const items = [
    { label: 'Municipio', value: `${summary.municipio}, ${summary.departamento}` },
    { label: 'DIVIPOLA', value: summary.divipola },
    { label: 'Region', value: summary.region },
    { label: 'Poblacion total', value: summary.poblacion_total?.toLocaleString('es-CO') },
    { label: 'Matricula total', value: summary.matricula_total?.toLocaleString('es-CO') },
    { label: 'ICFES promedio', value: summary.icfes?.promedio_global },
    { label: 'Total hurtos', value: summary.total_hurtos?.toLocaleString('es-CO') },
    { label: 'Total VIF', value: summary.total_vif?.toLocaleString('es-CO') },
    { label: 'Prestadores servicios', value: summary.prestadores_servicios?.toLocaleString('es-CO') },
  ]

  return (
    <div>
      <h3 className="section-title">Resumen Ejecutivo</h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {items.map((item) => (
          <div key={item.label} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 10px', background: 'var(--bg-card)', borderRadius: 6, border: '1px solid var(--border)' }}>
            <span style={{ color: 'var(--text-secondary)', fontSize: 12 }}>{item.label}</span>
            <span style={{ color: 'var(--text-primary)', fontSize: 12, fontWeight: 600 }}>{item.value ?? '---'}</span>
          </div>
        ))}
      </div>

      {summary.principales_hechos_victimizantes?.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <h4 style={{ color: 'var(--text-primary)', fontSize: 11, marginBottom: 8, textTransform: 'uppercase', letterSpacing: 1, fontWeight: 700 }}>
            Principales hechos victimizantes
          </h4>
          {summary.principales_hechos_victimizantes.map((h) => (
            <div key={h.hecho} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 10px', fontSize: 11, color: 'var(--text-secondary)' }}>
              <span>{h.hecho}</span>
              <span style={{ color: 'var(--semantic-negative)', fontWeight: 600 }}>{h.personas?.toLocaleString('es-CO')}</span>
            </div>
          ))}
          <div className="data-source" style={{ marginTop: 8 }}>
            Fuente: Unidad para las Victimas
          </div>
        </div>
      )}
    </div>
  )
}
