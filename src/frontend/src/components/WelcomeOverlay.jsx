import { useState, useEffect } from 'react'

const DISMISSED_KEY = 'observatorio-welcome-dismissed'

export default function WelcomeOverlay() {
  const [visible, setVisible] = useState(false)
  const [closing, setClosing] = useState(false)

  useEffect(() => {
    if (!localStorage.getItem(DISMISSED_KEY)) {
      setVisible(true)
    }
  }, [])

  const dismiss = () => {
    setClosing(true)
    setTimeout(() => {
      setVisible(false)
      localStorage.setItem(DISMISSED_KEY, '1')
    }, 300)
  }

  if (!visible) return null

  return (
    <div
      onClick={dismiss}
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 9999,
        background: 'rgba(0,0,0,0.55)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        opacity: closing ? 0 : 1,
        transition: 'opacity 0.3s ease',
        cursor: 'pointer',
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          background: 'var(--bg-primary)',
          borderRadius: 16,
          padding: '36px 40px',
          maxWidth: 520,
          width: '90%',
          boxShadow: '0 12px 40px rgba(0,0,0,0.25)',
          transform: closing ? 'scale(0.95)' : 'scale(1)',
          transition: 'transform 0.3s ease',
        }}
      >
        <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--accent-primary)', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 8 }}>
          Observatorio de Ciudades
        </div>
        <h1 style={{ fontSize: 28, fontWeight: 700, color: 'var(--text-primary)', lineHeight: 1.2, marginBottom: 8 }}>
          Apartado, Antioquia
        </h1>
        <p style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: 20 }}>
          Plataforma integral de datos territoriales que integra informacion de
          {' '}<strong>seguridad</strong>, <strong>educacion</strong>, <strong>salud</strong>,
          {' '}<strong>economia</strong> y <strong>gobierno</strong> del municipio de Apartado
          en la region de Uraba.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 24 }}>
          {[
            { n: '55', label: 'Tablas de datos' },
            { n: '123,270', label: 'Registros' },
            { n: '8', label: 'Dimensiones' },
            { n: '16+', label: 'Fuentes oficiales' },
          ].map((s) => (
            <div key={s.label} style={{ padding: '10px 14px', background: 'var(--bg-secondary)', borderRadius: 8, border: '1px solid var(--border)' }}>
              <div style={{ fontSize: 20, fontWeight: 700, color: 'var(--accent-primary)' }}>{s.n}</div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{s.label}</div>
            </div>
          ))}
        </div>

        <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 20, lineHeight: 1.5 }}>
          Fuentes: DANE, DNP-TerriData, Policia Nacional, ICFES, MinSalud, MinTIC, SECOP, INS-SIVIGILA, Unidad para las Victimas, Google Places, OpenStreetMap
        </div>

        <button
          onClick={dismiss}
          style={{
            width: '100%',
            padding: '12px 0',
            background: 'var(--accent-primary)',
            color: '#FFFFFF',
            border: 'none',
            borderRadius: 8,
            fontSize: 14,
            fontWeight: 600,
            cursor: 'pointer',
            fontFamily: 'inherit',
          }}
        >
          Explorar el observatorio
        </button>
      </div>
    </div>
  )
}
