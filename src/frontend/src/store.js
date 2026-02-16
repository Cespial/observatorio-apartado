import { create } from 'zustand'

const API = '/api'

const savedTheme = typeof window !== 'undefined'
  ? localStorage.getItem('observatorio-theme') || 'light'
  : 'light'
if (typeof document !== 'undefined') {
  document.documentElement.setAttribute('data-theme', savedTheme)
}

export const useStore = create((set, get) => ({
  theme: savedTheme,
  toggleTheme: () => {
    const next = get().theme === 'light' ? 'dark' : 'light'
    document.documentElement.setAttribute('data-theme', next)
    localStorage.setItem('observatorio-theme', next)
    set({ theme: next })
  },

  viewState: {
    longitude: -76.6258,
    latitude: 7.8833,
    zoom: 13,
    pitch: 45,
    bearing: -15,
  },
  setViewState: (vs) => set({ viewState: vs }),

  activeLayers: ['limite_municipal', 'osm_vias', 'google_places'],
  toggleLayer: (id) => set((s) => ({
    activeLayers: s.activeLayers.includes(id)
      ? s.activeLayers.filter((l) => l !== id)
      : [...s.activeLayers, id],
  })),

  layerData: {},
  summary: null,
  securityMatrix: null,
  placesCategories: null,
  icfesData: null,
  victimasData: null,
  crossvarData: null,
  saludData: null,
  economiaData: null,
  gobiernoData: null,
  activePanel: 'overview',
  setActivePanel: (p) => set({ activePanel: p }),

  fetchSummary: async () => {
    const r = await fetch(`${API}/stats/summary`)
    set({ summary: await r.json() })
  },
  fetchLayerGeoJSON: async (id) => {
    if (get().layerData[id]) return
    const r = await fetch(`${API}/layers/${id}/geojson`)
    const d = await r.json()
    set((s) => ({ layerData: { ...s.layerData, [id]: d } }))
  },
  fetchManzanas: async () => {
    if (get().layerData.manzanas) return
    const r = await fetch(`${API}/geo/manzanas?limit=5000`)
    const d = await r.json()
    set((s) => ({ layerData: { ...s.layerData, manzanas: d } }))
  },
  fetchPlaces: async () => {
    if (get().layerData.places) return
    const [p, c] = await Promise.all([
      fetch(`${API}/geo/places?limit=2000`),
      fetch(`${API}/geo/places/categories`),
    ])
    const pData = await p.json()
    const cData = await c.json()
    set((s) => ({
      layerData: { ...s.layerData, places: pData },
      placesCategories: cData,
    }))
  },
  fetchPlacesHeatmap: async () => {
    if (get().layerData.placesHeatmap) return
    const r = await fetch(`${API}/geo/places/heatmap`)
    const d = await r.json()
    set((s) => ({ layerData: { ...s.layerData, placesHeatmap: d } }))
  },
  fetchSecurityMatrix: async () => {
    if (get().securityMatrix) return
    const r = await fetch(`${API}/crossvar/security-matrix`)
    const d = await r.json()
    set({ securityMatrix: d.data })
  },
  fetchIcfes: async () => {
    if (get().icfesData) return
    const r = await fetch(`${API}/indicators/icfes?aggregate=periodo`)
    set({ icfesData: await r.json() })
  },
  fetchVictimas: async () => {
    if (get().victimasData) return
    const r = await fetch(`${API}/indicators/victimas?aggregate=hecho`)
    set({ victimasData: await r.json() })
  },
  fetchCrossvar: async (vx, vy) => {
    const r = await fetch(`${API}/crossvar/scatter?var_x=${vx}&var_y=${vy}`)
    set({ crossvarData: await r.json() })
  },
  fetchSalud: async () => {
    if (get().saludData) return
    const [td, ir, sv] = await Promise.all([
      fetch(`${API}/indicators/terridata?dimension=Salud`),
      fetch(`${API}/indicators/salud/irca`),
      fetch(`${API}/indicators/salud/sivigila/resumen`),
    ])
    set({
      saludData: {
        terridata: await td.json(),
        irca: await ir.json(),
        sivigila: await sv.json(),
      },
    })
  },
  fetchEconomia: async () => {
    if (get().economiaData) return
    const [inet, sec, tur, td] = await Promise.all([
      fetch(`${API}/indicators/economia/internet/serie`),
      fetch(`${API}/indicators/economia/secop`),
      fetch(`${API}/indicators/economia/turismo`),
      fetch(`${API}/indicators/terridata?dimension=${encodeURIComponent('Economía')}`),
    ])
    set({
      economiaData: {
        internet: await inet.json(),
        secop: await sec.json(),
        turismo: await tur.json(),
        terridata_economia: await td.json(),
      },
    })
  },
  fetchGobierno: async () => {
    if (get().gobiernoData) return
    const [fin, des, dig, pob] = await Promise.all([
      fetch(`${API}/indicators/gobierno/finanzas`),
      fetch(`${API}/indicators/gobierno/desempeno`),
      fetch(`${API}/indicators/gobierno/digital`),
      fetch(`${API}/indicators/gobierno/pobreza`),
    ])
    set({
      gobiernoData: {
        finanzas: await fin.json(),
        desempeno: await des.json(),
        digital: await dig.json(),
        pobreza: await pob.json(),
      },
    })
  },
}))
