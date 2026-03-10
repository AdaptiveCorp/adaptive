/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        dark: {
          900: '#0a0e1a',
          800: '#0f1526',
          700: '#151d35',
          600: '#1c2644',
          500: '#243055',
        },
        brand: {
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
        },
        danger: {
          400: '#f87171',
          500: '#ef4444',
        },
        success: {
          400: '#4ade80',
          500: '#22c55e',
        },
        warning: {
          400: '#fbbf24',
          500: '#f59e0b',
        },
      },
    },
  },
  plugins: [],
}
