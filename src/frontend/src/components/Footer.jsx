export default function Footer() {
  const sources = ['ComputTrabajo', 'elempleo', 'Indeed', 'Comfama', 'LinkedIn', 'DANE', 'DNP-TerriData', 'ICFES', 'Google Places']

  return (
    <footer
      style={{
        height: 32,
        background: 'var(--bg-primary)',
        borderTop: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px',
        flexShrink: 0,
        fontSize: 11,
        color: 'var(--text-secondary)',
      }}
    >
      <div>
        <span style={{ fontWeight: 600, marginRight: 4 }}>Fuentes:</span>
        {sources.map((s, i) => (
          <span key={s}>
            {s}{i < sources.length - 1 && <span style={{ margin: '0 4px', color: 'var(--text-muted)', opacity: 0.6 }}>&middot;</span>}
          </span>
        ))}
      </div>
      <div>
        Observatorio Laboral de Uraba &copy; 2026 <span style={{ margin: '0 4px', opacity: 0.5 }}>&middot;</span> Datos actualizados diariamente
      </div>
    </footer>
  )
}
