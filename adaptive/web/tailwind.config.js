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
          300: '#7DD3FC',
          400: '#38BDF8',
          500: '#0EA5E9',
          600: '#0284C7',
          700: '#0369A1',
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
