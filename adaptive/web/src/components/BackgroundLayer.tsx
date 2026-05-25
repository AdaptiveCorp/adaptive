export function BackgroundLayer() {
  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      zIndex: 0,
      backgroundColor: 'var(--body-bg)',
      backgroundImage: 'var(--body-bg-image)',
      backgroundSize: '100% 100%, 30px 30px',
      transition: 'background-color 0.2s ease',
      pointerEvents: 'none',
    }} />
  )
}
