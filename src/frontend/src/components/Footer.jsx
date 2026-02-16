export default function Footer() {
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
        color: 'var(--text-muted)',
      }}
    >
      <div>
        Fuentes: DANE, DNP-TerriData, Policia Nacional, ICFES, MinSalud, MinEducacion, Google Places, OSM
      </div>
      <div>
        Observatorio de Ciudades &copy; 2026 &middot; Ultima actualizacion: Feb 2026
      </div>
    </footer>
  )
}
