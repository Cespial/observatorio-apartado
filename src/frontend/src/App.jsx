import { useEffect, useMemo } from 'react'
import { useStore } from './store'
import Header from './components/Header'
import KPICards from './components/KPICards'
import MapView from './components/MapView'
import LayerPanel from './components/LayerPanel'
import SidePanel from './components/SidePanel'
import Footer from './components/Footer'
import WelcomeOverlay from './components/WelcomeOverlay'

export default function App() {
  const { summary, fetchSummary } = useStore()

  const isEmbed = useMemo(() => {
    const params = new URLSearchParams(window.location.search)
    return params.get('embed') === 'true'
  }, [])

  useEffect(() => { fetchSummary() }, [])

  return (
    <>
      {!isEmbed && <WelcomeOverlay />}
      {!isEmbed && <Header />}
      {!isEmbed && <KPICards summary={summary} />}
      <div className="main-layout" style={{ flex: 1, display: 'flex', position: 'relative', overflow: 'hidden' }}>
        <div style={{ flex: 1, position: 'relative' }}>
          <MapView />
          {!isEmbed && <LayerPanel />}
        </div>
        <SidePanel />
      </div>
      {!isEmbed && <Footer />}
    </>
  )
}
