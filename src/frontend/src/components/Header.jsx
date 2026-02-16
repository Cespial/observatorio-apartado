import { useStore } from '../store'

export default function Header() {
  const theme = useStore((s) => s.theme)
  const toggleTheme = useStore((s) => s.toggleTheme)
  const showToast = useStore((s) => s.showToast)
  const catalogSummary = useStore((s) => s.catalogSummary)

  return (
    <header
      style={{
        height: 56,
        background: 'var(--bg-primary)',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px',
        flexShrink: 0,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <div>
          <div style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '0.02em' }}>
            Observatorio de Ciudades
          </div>
          <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
            Plataforma de datos territoriales
          </div>
        </div>
        <div style={{ width: 1, height: 32, background: 'var(--border)', margin: '0 8px' }} />
        <div>
          <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--accent-primary)' }}>
            Apartado, Antioquia
          </div>
          <div className="font-mono" style={{ fontSize: 11, color: 'var(--text-muted)' }}>
            DANE 05045
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <div className="header-desktop-info" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span
            style={{
              width: 7, height: 7, borderRadius: '50%',
              background: 'var(--semantic-positive)',
              display: 'inline-block',
            }}
          />
          <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
            {catalogSummary
              ? `${catalogSummary.tables} tablas \u00B7 ${catalogSummary.records?.toLocaleString('es-CO')} registros`
              : 'Cargando...'}
          </span>
        </div>

        {/* Theme toggle */}
        <button
          onClick={toggleTheme}
          aria-label={theme === 'light' ? 'Cambiar a modo oscuro' : 'Cambiar a modo claro'}
          title={theme === 'light' ? 'Modo oscuro' : 'Modo claro'}
          style={{
            background: 'var(--bg-tertiary)',
            border: '1px solid var(--border)',
            borderRadius: 6,
            width: 32,
            height: 32,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            fontSize: 16,
            color: 'var(--text-secondary)',
          }}
        >
          {theme === 'light' ? '\u263E' : '\u2600'}
        </button>

        {/* Share / Embed */}
        <button
          onClick={() => {
            const url = `${window.location.origin}${window.location.pathname}?embed=true`
            navigator.clipboard.writeText(url)
            showToast('URL de embed copiada al portapapeles')
          }}
          aria-label="Copiar URL de embed"
          title="Copiar URL embed"
          style={{
            background: 'var(--bg-tertiary)',
            border: '1px solid var(--border)',
            borderRadius: 6,
            width: 32,
            height: 32,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            fontSize: 14,
            color: 'var(--text-secondary)',
          }}
        >
          &lt;/&gt;
        </button>
      </div>
    </header>
  )
}
