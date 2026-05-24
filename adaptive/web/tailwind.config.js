/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans:    ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
        display: ['"IBM Plex Mono"', 'monospace'],
        mono:    ['"Fira Code"', 'monospace'],
      },
      colors: {
        dark: {
          900: '#06101C',
          800: '#0A1728',
          700: '#0F2034',
          600: '#162840',
          500: '#1D3250',
        },
        brand: {
          300: 'rgb(var(--brand-300-rgb) / <alpha-value>)',
          400: 'rgb(var(--brand-400-rgb) / <alpha-value>)',
          500: 'rgb(var(--brand-500-rgb) / <alpha-value>)',
          600: 'rgb(var(--brand-600-rgb) / <alpha-value>)',
          700: 'rgb(var(--brand-700-rgb) / <alpha-value>)',
        },
        danger: {
          400: '#FB7185',
          500: '#F43F5E',
        },
        success: {
          400: '#34D399',
          500: '#10B981',
        },
        warning: {
          400: '#FBBF24',
          500: '#F59E0B',
        },
      },
    },
  },
  plugins: [],
}
