export function SkeletonKPI({ count = 4 }) {
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="skeleton skeleton-kpi" style={{ flex: '1 1 45%', minWidth: 120 }} />
      ))}
    </div>
  )
}

export function SkeletonChart() {
  return <div className="skeleton skeleton-chart" />
}

export function SkeletonBars({ count = 5 }) {
  return (
    <div style={{ padding: '8px 0' }}>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="skeleton skeleton-bar" />
      ))}
    </div>
  )
}

export function SkeletonTab() {
  return (
    <div style={{ padding: 4 }}>
      <div className="skeleton" style={{ width: '40%', height: 16, marginBottom: 16 }} />
      <SkeletonKPI count={4} />
      <div style={{ marginTop: 16 }}>
        <div className="skeleton" style={{ width: '55%', height: 12, marginBottom: 10 }} />
        <SkeletonChart />
      </div>
      <div style={{ marginTop: 12 }}>
        <div className="skeleton" style={{ width: '45%', height: 12, marginBottom: 10 }} />
        <SkeletonBars count={4} />
      </div>
    </div>
  )
}
