import { useState, useEffect, useCallback, useRef } from 'react'
import { useStore } from '../../store'
import DashboardCard from './DashboardCard'

function debounce(fn, ms) {
  let id
  return (...args) => {
    clearTimeout(id)
    id = setTimeout(() => fn(...args), ms)
  }
}

export default function OfertasExplorer() {
  const {
    ofertasExplorer, ofertasExplorerLoading,
    fetchOfertasExplorer,
    empleoData,
  } = useStore()

  const [search, setSearch] = useState('')
  const [sector, setSector] = useState('')
  const [fuente, setFuente] = useState('')
  const [tipoContrato, setTipoContrato] = useState('')
  const [modalidad, setModalidad] = useState('')
  const [expandedId, setExpandedId] = useState(null)

  // Debounced search
  const debouncedFetch = useRef(
    debounce((params) => fetchOfertasExplorer(params), 400)
  ).current

  useEffect(() => {
    fetchOfertasExplorer({ page: 1 })
  }, [])

  const handleSearch = (val) => {
    setSearch(val)
    debouncedFetch({ page: 1, search: val, sector, fuente, tipo_contrato: tipoContrato, modalidad })
  }

  const handleFilter = (key, val, setter) => {
    setter(val)
    fetchOfertasExplorer({ page: 1, search, sector, fuente, tipo_contrato: tipoContrato, modalidad, [key]: val || null })
  }

  const handlePage = (p) => {
    fetchOfertasExplorer({ page: p, search, sector, fuente, tipo_contrato: tipoContrato, modalidad })
  }

  const handleExportCSV = () => {
    if (!ofertasExplorer?.items?.length) return
    const headers = ['Titulo', 'Empresa', 'Sector', 'Salario', 'Municipio', 'Fecha', 'Fuente']
    const rows = ofertasExplorer.items.map(o => [
      o.titulo, o.empresa || '', o.sector || '', o.salario_texto || '',
      o.municipio, o.fecha_publicacion || '', o.fuente,
    ])
    const csv = [headers, ...rows].map(r => r.map(c => `"${String(c).replace(/"/g, '""')}"`).join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'ofertas_laborales.csv'
    a.click()
    URL.revokeObjectURL(url)
  }

  // Get sector options from empleoData
  const sectorOptions = empleoData?.sectores?.map(s => s.sector) || []
  const fuenteOptions = empleoData?.stats?.por_fuente?.map(f => f.fuente) || []

  const data = ofertasExplorer
  const items = data?.items || []

  const selectStyle = {
    padding: '6px 10px', borderRadius: 6, border: '1px solid var(--border)',
    background: 'var(--bg-secondary)', color: 'var(--text-primary)',
    fontSize: 12, fontFamily: 'inherit',
  }

  return (
    <DashboardCard span={3} title="Explorador de Ofertas"
      actions={
        <button
          onClick={handleExportCSV}
          style={{
            padding: '4px 10px', borderRadius: 4, border: '1px solid var(--border)',
            background: 'var(--bg-secondary)', color: 'var(--text-secondary)',
            fontSize: 11, cursor: 'pointer', fontFamily: 'inherit',
          }}
        >
          CSV
        </button>
      }
    >
      {/* Filters */}
      <div className="directory-filters" style={{ marginBottom: 12 }}>
        <input
          type="text"
          placeholder="Buscar por titulo o descripcion..."
          value={search}
          onChange={e => handleSearch(e.target.value)}
          style={{ ...selectStyle, flex: 1, minWidth: 200 }}
        />
        <select value={sector} onChange={e => handleFilter('sector', e.target.value, setSector)} style={selectStyle}>
          <option value="">Todos los sectores</option>
          {sectorOptions.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <select value={fuente} onChange={e => handleFilter('fuente', e.target.value, setFuente)} style={selectStyle}>
          <option value="">Todas las fuentes</option>
          {fuenteOptions.map(f => <option key={f} value={f}>{f}</option>)}
        </select>
        <select value={tipoContrato} onChange={e => handleFilter('tipo_contrato', e.target.value, setTipoContrato)} style={selectStyle}>
          <option value="">Todo contrato</option>
          <option value="Indefinido">Indefinido</option>
          <option value="Fijo">Fijo</option>
          <option value="Prestacion de servicios">Prestacion de servicios</option>
          <option value="Obra o labor">Obra o labor</option>
          <option value="Aprendizaje">Aprendizaje</option>
        </select>
        <select value={modalidad} onChange={e => handleFilter('modalidad', e.target.value, setModalidad)} style={selectStyle}>
          <option value="">Toda modalidad</option>
          <option value="Presencial">Presencial</option>
          <option value="Remoto">Remoto</option>
          <option value="Hibrido">Hibrido</option>
        </select>
      </div>

      {/* Table */}
      <div style={{ overflowX: 'auto', maxHeight: 500, overflowY: 'auto' }}>
        <table className="ofertas-table directory-table">
          <thead>
            <tr>
              <th>Titulo</th>
              <th>Empresa</th>
              <th>Sector</th>
              <th>Salario</th>
              <th>Municipio</th>
              <th>Fecha</th>
              <th>Fuente</th>
            </tr>
          </thead>
          <tbody>
            {ofertasExplorerLoading && items.length === 0 ? (
              <tr><td colSpan={7} style={{ textAlign: 'center', padding: 24, color: 'var(--text-muted)' }}>Cargando...</td></tr>
            ) : items.length === 0 ? (
              <tr><td colSpan={7} style={{ textAlign: 'center', padding: 24, color: 'var(--text-muted)' }}>Sin resultados</td></tr>
            ) : items.map(o => (
              <>
                <tr key={o.id} onClick={() => setExpandedId(expandedId === o.id ? null : o.id)}>
                  <td style={{ maxWidth: 250, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontWeight: 500 }}>
                    {o.titulo}
                  </td>
                  <td>{o.empresa || '—'}</td>
                  <td><span className="badge badge-blue">{o.sector || 'Otro'}</span></td>
                  <td>{o.salario_texto || '—'}</td>
                  <td>{o.municipio}</td>
                  <td style={{ whiteSpace: 'nowrap' }}>{o.fecha_publicacion || '—'}</td>
                  <td><span className="badge badge-gray">{o.fuente}</span></td>
                </tr>
                {expandedId === o.id && (
                  <tr key={`detail-${o.id}`}>
                    <td colSpan={7}>
                      <div className="ofertas-detail">
                        {o.descripcion && (
                          <p style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 8, maxHeight: 120, overflow: 'auto', lineHeight: 1.5 }}>
                            {o.descripcion.slice(0, 500)}{o.descripcion.length > 500 ? '...' : ''}
                          </p>
                        )}
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 8 }}>
                          {o.skills?.map((s, i) => (
                            <span key={i} className="badge badge-blue">{s}</span>
                          ))}
                        </div>
                        <div style={{ display: 'flex', gap: 16, fontSize: 11, color: 'var(--text-muted)' }}>
                          {o.nivel_experiencia && <span>Experiencia: <b>{o.nivel_experiencia}</b></span>}
                          {o.tipo_contrato && <span>Contrato: <b>{o.tipo_contrato}</b></span>}
                          {o.nivel_educativo && <span>Educacion: <b>{o.nivel_educativo}</b></span>}
                          {o.modalidad && <span>Modalidad: <b>{o.modalidad}</b></span>}
                        </div>
                        {o.enlace && (
                          <a href={o.enlace} target="_blank" rel="noopener noreferrer"
                            style={{ fontSize: 11, color: 'var(--accent-primary)', marginTop: 6, display: 'inline-block' }}>
                            Ver oferta original
                          </a>
                        )}
                      </div>
                    </td>
                  </tr>
                )}
              </>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {data && data.total_pages > 1 && (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 8, marginTop: 12, fontSize: 12 }}>
          <button
            onClick={() => handlePage(data.page - 1)}
            disabled={data.page <= 1}
            style={{
              padding: '4px 10px', borderRadius: 4, border: '1px solid var(--border)',
              background: 'var(--bg-secondary)', color: 'var(--text-secondary)',
              cursor: data.page <= 1 ? 'default' : 'pointer', opacity: data.page <= 1 ? 0.5 : 1,
              fontFamily: 'inherit',
            }}
          >
            Anterior
          </button>
          <span style={{ color: 'var(--text-secondary)' }}>
            Pagina {data.page} de {data.total_pages} ({data.total} ofertas)
          </span>
          <button
            onClick={() => handlePage(data.page + 1)}
            disabled={data.page >= data.total_pages}
            style={{
              padding: '4px 10px', borderRadius: 4, border: '1px solid var(--border)',
              background: 'var(--bg-secondary)', color: 'var(--text-secondary)',
              cursor: data.page >= data.total_pages ? 'default' : 'pointer',
              opacity: data.page >= data.total_pages ? 0.5 : 1,
              fontFamily: 'inherit',
            }}
          >
            Siguiente
          </button>
        </div>
      )}
    </DashboardCard>
  )
}
