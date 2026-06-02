/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        industrial: {
          bg: '#0a0e14',
          panel: '#111722',
          card: '#161d2b',
          border: '#1f2937',
          accent: '#0ea5e9',
          cyan: '#22d3ee',
          green: '#10b981',
          amber: '#f59e0b',
          red: '#ef4444',
          text: '#e5e7eb',
          muted: '#94a3b8',
        },
      },
      boxShadow: {
        glow: '0 0 20px rgba(14,165,233,0.25)',
        'glow-red': '0 0 20px rgba(239,68,68,0.3)',
      },
      fontFamily: {
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
      },
      keyframes: {
        pulseSlow: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.6' },
        },
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(6px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        'pulse-slow': 'pulseSlow 2.5s ease-in-out infinite',
        'fade-in': 'fadeIn 0.4s ease-out',
      },
    },
  },
  plugins: [],
}
