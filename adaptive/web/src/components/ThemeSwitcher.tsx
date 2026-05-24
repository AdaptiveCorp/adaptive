import { Moon, Sun } from 'lucide-react'
import { useTheme } from '../context/ThemeContext'

export function ThemeSwitcher() {
  const { theme, toggle } = useTheme()

  return (
    <button
      onClick={toggle}
      title={theme === 'dark' ? 'Passer en clair' : 'Passer en sombre'}
      style={{
        width: 32,
        height: 32,
        borderRadius: 6,
        border: '1px solid var(--border-base)',
        background: 'var(--bg-input)',
        color: 'var(--text-muted)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        cursor: 'pointer',
        transition: 'color 0.15s ease, background 0.15s ease, border-color 0.15s ease',
        flexShrink: 0,
      }}
    >
      {theme === 'dark' ? <Sun size={14} /> : <Moon size={14} />}
    </button>
  )
}
